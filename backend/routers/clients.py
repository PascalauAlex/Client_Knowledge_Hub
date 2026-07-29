from starlette.concurrency import run_in_threadpool

import models
from database import DbSession
from fastapi import APIRouter, HTTPException
from fastapi import  status
from sqlalchemy import select, delete as sql_delete
from models import Client
from routers import documents
from schemas import ClientCreate, ClientResponse, ClientUpdate
from utils.auth import CurrentUser
from utils.documents_utils import delete_document_from_disk

router = APIRouter(prefix="",tags=["clients"])


@router.get(path="",response_model=list[ClientResponse],status_code=status.HTTP_200_OK)
async def get_clients(current_user : CurrentUser , db: DbSession):
    result = await db.execute(select(models.Client))
    clients = result.scalars().all()

    return clients


@router.post(path="",
             response_model=ClientResponse,
             status_code=status.HTTP_201_CREATED
             )
async def create_client(
        client : ClientCreate,
        current_user : CurrentUser,
        db: DbSession
):
    result = await db.execute(select(models.Client).where(models.Client.name == client.name))

    existing_client = result.scalars().first()

    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The client name exists"
        )

    new_client = Client(
        name=client.name,
        email=client.email,
        created_by_id=current_user.id,
        created_by=current_user,
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client,attribute_names=["created_by"])
    return new_client


@router.get(path="/{client_id}",
            response_model=ClientResponse,
            status_code=status.HTTP_200_OK)
async def get_client(
        client_id: int,
        current_user : CurrentUser,
        db: DbSession
):
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    client = result.scalars().first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client was not found"
        )

    if client.created_by != current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No client with the current id= {client_id}"
        )
    
    return client

@router.patch(path="/{cliend_id}",response_model=ClientResponse,status_code=status.HTTP_200_OK)
async def client_partial_update(client_id : int,
                                current_user: CurrentUser,
                                client_data: ClientUpdate,
                                db:DbSession
):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,"You are not allowed to modify this user")

    client.name = client_data.name
    client.email = client_data.email

    await db.commit()
    await db.refresh(client)
    return client


@router.delete(path="/{client_id}",status_code=status.HTTP_200_OK)
async def delete_client(client_id : int, db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(models.Client).where(models.Client.id == client_id))
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    if client.created_by_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,detail="Not found.")

    result = await db.execute(select(models.Document).where(models.Document.client_id == client_id))
    documents = result.scalars().all()

    await db.execute(sql_delete(models.Client).where(models.Client.id == client_id))

    await db.commit()

    for doc in documents:
        await run_in_threadpool(delete_document_from_disk,doc.file)

    return {"message":"All clients and documents were removed"}













