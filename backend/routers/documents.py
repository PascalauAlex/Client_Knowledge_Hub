from pydantic import Field
from fastapi import APIRouter, status, UploadFile, Depends, HTTPException
from typing import Annotated
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.sql.functions import current_user
from starlette.concurrency import run_in_threadpool
import models
from config import settings
from schemas import DocumentResponse
from utils.auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession
from utils.documents_utils import process_document, delete_document_from_disk, ACCEPTED_MIME
from database import get_db

router = APIRouter()



@router.post(path="/upload",status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile,
                          db: Annotated[AsyncSession, Depends(get_db)],
                          current_user: CurrentUser,
                          client_id:int,
                          name:str
                          ):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must provide a file.")

    accepted_extensions = tuple(ACCEPTED_MIME.values())

    if not file.filename.endswith(accepted_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The file extensions must be in {accepted_extensions}"
        )
    content = await file.read()
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid client id"
        )
    if client.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are unauthorized to upload this document to this client"
        )

    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The size of the file cannot be bigger than 100 MB"
        )

    filename = await run_in_threadpool(process_document,content)

    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file must have the following extensions: (.pdf, .doc, .docx, .xlsx, .csv)"
        )

    new_document = models.Document(
        name=name,
        client_id=client_id,
        file=filename
    )

    db.add(new_document)
    await db.commit()
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

    await run_in_threadpool(delete_document_from_disk,document_name)

    await db.commit()
    return {"success":"The document was deleted successfully"}

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

    return document

@router.get("",status_code=status.HTTP_200_OK,response_model=list[DocumentResponse])
async def get_documents(db:Annotated[AsyncSession,Depends(get_db)],current_user:CurrentUser, client_id : int):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))

    client = result.scalars().first()

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Client was not found")
    if client.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed to access this document")

    result = await db.execute(select(models.Document).where(models.Document.client_id == client_id))

    documents = result.scalars().all()


    return documents

@router.patch("",status_code=status.HTTP_200_OK,response_model=DocumentResponse)
async def update_document(
        new_name : Annotated[str,Field(min_length=3,max_length=250)],
        db:Annotated[AsyncSession,Depends(get_db)],
        current_user:CurrentUser,
        client_id: int,
        document_id : int):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()

    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND,"The client was not found")

    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,"You are not authorized to modify this document")

    result = await db.execute(select(models.Document).where(models.Document.id == document_id))

    document = result.scalars().first()

    if not document:
        raise HTTPException(status.HTTP_404_NOT_FOUND,"The document was not found")

    document.name = new_name

    await db.commit()
    await db.refresh(document)

    return document













