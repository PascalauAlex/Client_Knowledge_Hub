from sqlalchemy.orm import joinedload
import models
from agents.rag import  generate_answer
from database import DbSession
from fastapi import APIRouter, HTTPException
from fastapi import status
from sqlalchemy import select, delete as sql_delete
from models import Client
from schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    DocumentResponse,
)
from utils.auth import CurrentUser
from utils.documents_utils import ACCEPTED_MIME
from utils.image_utils import create_presigned_url, delete_document_s3
from botocore.exceptions import ClientError

router = APIRouter(prefix="", tags=["clients"])


@router.get(
    path="", response_model=list[ClientResponse], status_code=status.HTTP_200_OK
)
async def get_clients(current_user: CurrentUser, db: DbSession):
    result = await db.execute(select(models.Client).where(models.Client.created_by_id == current_user.id))
    clients = result.scalars().all()
    return clients


@router.post(
    path="", response_model=ClientResponse, status_code=status.HTTP_201_CREATED
)
async def create_client(client: ClientCreate, current_user: CurrentUser, db: DbSession):
    result = await db.execute(
        select(models.Client).where(models.Client.name == client.name)
    )

    existing_client = result.scalars().first()

    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The client name already exists"
        )

    new_client = Client(
        name=client.name,
        email=client.email,
        created_by_id=current_user.id,
        created_by=current_user,
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client, attribute_names=["created_by"])
    return new_client


@router.get(
    path="/{client_id}", response_model=ClientResponse, status_code=status.HTTP_200_OK
)
async def get_client(client_id: int, current_user: CurrentUser, db: DbSession):
    result = await db.execute(
        select(models.Client)
        .where(models.Client.id == client_id)
        .options(joinedload(models.Client.created_by))
    )
    client = result.scalars().first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client was not found"
        )

    if client.created_by.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No client with the current id: {client_id}",
        )

    return client


@router.patch(
    path="/{cliend_id}", response_model=ClientResponse, status_code=status.HTTP_200_OK
)
async def client_partial_update(
    client_id: int, current_user: CurrentUser, client_data: ClientUpdate, db: DbSession
):
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    client = result.scalars().first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    if client.created_by_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "You are not allowed to modify this user"
        )

    client.name = client_data.name
    client.email = client_data.email

    await db.commit()
    await db.refresh(client)
    return client


@router.delete(path="/{client_id}", status_code=status.HTTP_200_OK)
async def delete_client(client_id: int, db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not found.")

    result = await db.execute(
        select(models.Document).where(models.Document.client_id == client_id)
    )
    documents = result.scalars().all()

    await db.execute(sql_delete(models.Client).where(models.Client.id == client_id))

    await db.commit()

    for doc in documents:
        try:
            await delete_document_s3(filename=doc.file)
            await db.execute(
                sql_delete(models.Document).where(models.Document.id == doc.id)
            )
        except ClientError as err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error while deleting document :{doc.file} from S3. Error:{err}",
            )

    return {"message": "Client and related documents were removed"}


@router.get(
    path="/documents/{client_id}",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_client_documents(
    db: DbSession, current_user: CurrentUser, client_id: int
):
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    client = result.scalars().first()

    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")

    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Client not found")

    result = await db.execute(
        select(models.Document).where(models.Document.client_id == client.id)
    )

    client_documents = result.scalars().all()

    if not client_documents:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documents not found")

    for doc in client_documents:
        object_name = doc.file
        mime_type = ""

        for mime, ext in ACCEPTED_MIME.items():
            if object_name.endswith(ext):
                mime_type = mime

        object_name = f"files/{object_name}"
        presigned_url = create_presigned_url(
            object_name=object_name, response_type=mime_type
        )
        if presigned_url is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate presigned url for the current file, please try again.",
            )
        doc.file = presigned_url

    return client_documents


@router.post("/{client_id}/query")
async def query_documents(
    db: DbSession, client_id: int, query: str, current_user: CurrentUser
):
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    client = result.scalars().first()

    if not client or client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")

    answer = await generate_answer(db=db, query=query, client_id=client_id)

    return answer
