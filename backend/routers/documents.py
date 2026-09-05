from botocore.exceptions import ClientError
from fastapi import APIRouter, status, UploadFile, Depends, HTTPException
from typing import Annotated, Literal
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.sql.functions import current_user
from starlette.concurrency import run_in_threadpool
import models
from agents.rag import DocumentLoader, ReportProcessor, embedd, save_embeddings
from config import settings
from schemas import DocumentResponse
from utils.auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession
from utils.documents_utils import process_document, ACCEPTED_MIME
from database import get_db
from utils.image_utils import upload_file_s3, delete_document_s3, create_presigned_url
from database import DbSession
from utils.aws_utils import get_object
from agents.structured_invoice_generator import structured_invoice_summary

router = APIRouter()



@router.post(path="/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(name: str,
                          client_id: int,
                          file: UploadFile,
                          doc_type: Literal["invoice", "contract", "report"],
                          db: Annotated[AsyncSession, Depends(get_db)],
                          current_user: CurrentUser,
                          ):
    # Ensure document type is within ["report","invoice","contract"]
    # TODO : Suport invoice and contract doc type
    if doc_type != "report":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only 'report' documents are supported for now.")

    # Check document extension and accept only the processable ones
    accepted_extensions = tuple(ACCEPTED_MIME.values())
    if not file.filename or not file.filename.endswith(accepted_extensions):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"The file extensions must be in {accepted_extensions}"
        )

    content = await file.read()

    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No client id")

    # Check if the passed client_id belongs to the authenticated user
    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized to upload this document to this client")

    # Enforce max file size ( see settings for exact supported size)
    if len(content) > settings.max_file_size:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The size of the file cannot be bigger than 100 MB")

    # Process document
    processed_file, filename, extension = await run_in_threadpool(process_document, content)

    if filename is None or extension is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file must have the following extensions: (.pdf, .doc, .docx, .xlsx, .csv)")


    # Upload document to S3 storage
    try:
        await upload_file_s3(processed_file, filename)
    except ClientError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while uploading to S3 {err}"
        ) from err

    # Create a new object
    new_document = models.Document(
        name=name,
        client_id=client_id,
        file=filename,
        extension_type=extension,
        type=doc_type
    )
    db.add(new_document)
    # Atomic transaction
    try:
        await db.flush()  # obtain document_id without commit
        # Document loader -> returns Document for processing
        loaded = DocumentLoader(extension=extension, file_bytes=processed_file).load_document()

        match new_document.type:
            case "report":
                chunks = ReportProcessor().recursive_chunking(loaded)

        if not chunks:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "The document contains no extractable text.")

        # Generate embeddings and save them to the database
        embeddings = await embedd(chunks=chunks)
        await save_embeddings(
            db=db,
            chunks=chunks,
            embeddings=embeddings,
            document_id=new_document.id,
            client_id=new_document.client_id,
        )
        await db.commit()

    except HTTPException:
        await db.rollback()
        await delete_document_s3(filename)
        raise
    except Exception as err:
        await db.rollback()
        await delete_document_s3(filename)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to process document: {err}") from err

    await db.refresh(new_document)
    return new_document

@router.delete("/delete",status_code=status.HTTP_200_OK)
async def delete_document(document_id: int,
                          db:Annotated[AsyncSession, Depends(get_db),current_user],
                          current_user:CurrentUser,
                          client_id:int):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))

    client = result.scalars().first()

    if client is None or client.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document (or Client) not found"
        )
    result = await db.execute(select(models.Document).where(models.Document.id == document_id))
    document = result.scalars().first()

    if document is None or document.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The document was not found"
        )
    document_name = document.file

    await db.execute(sql_delete(models.Document).where(models.Document.id == document_id))
    try:
        response =await delete_document_s3(filename=document_name)
    except ClientError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while deleting document {document_name} from S3: {err}"
        )

    await db.commit()
    return {"success":"The document was deleted successfully"}


@router.get("/document_summary")
async def get_document_summary(document_id: int, db: DbSession, current_user : CurrentUser, client_id : int):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="Client not found")

    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Client not found")

    result = await db.execute(select(models.Document).where(models.Document.id == document_id))
    document = result.scalars().first()

    if not document:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Document was not found")

    try:
        s3_doc = await run_in_threadpool(get_object,document.file)
    except ClientError as err:
        print("Error while fetching the document from S3")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not fetch document {document.name} from s3")

    if not s3_doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="The current file was not found!")
    structured_invoice = None

    match document.type:
        case 'invoice':
            structured_invoice = await run_in_threadpool(structured_invoice_summary,document.file,s3_doc)
    #TODO : Implement logic for other types of documents

    summary = {"summary" : structured_invoice if structured_invoice else "No summary"}

    if not structured_invoice:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="The ")


    return summary






@router.get("/{document_id}",status_code=status.HTTP_200_OK, response_model=DocumentResponse)
async def get_document(document_id: int , db: Annotated[AsyncSession,Depends(get_db)],current_user: CurrentUser, client_id:int):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()

    if client.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized")

    result = await db.execute(select(models.Document).where(models.Document.id == document_id))
    document = result.scalars().first()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUNDM,
            detail="The document was not found"
        )
    object_name = document.file
    if not object_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The document was not found"
        )

    mime_type = ""
    for mime , ext in ACCEPTED_MIME.items():
        if object_name.endswith(ext):
            mime_type = mime


    object_name = f"files/{object_name}"
    presigned_url = create_presigned_url(object_name=object_name,response_type=mime_type)
    if presigned_url is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate presigned url for the current file, please try again."
        )

    document.file = presigned_url

    return document


























