from http.client import responses

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sympy.polys.subresultants_qq_zz import res

import models
from tests.conftest import auth_header, create_test_user, login_user, create_test_client
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
import logging

@pytest.mark.anyio
async def test_create_client_success(authenticated_client : AsyncClient, db_session: AsyncSession):
    client = await create_test_client(authenticated_client)
    assert client.get("name") == "test_client"
    assert client.get("email") == "client@test.com"
    assert client.get("id")
    print(client.values())
    # Object session get invalidated
    db_session.expire_all()
    result = await db_session.execute(
        select(models.Client)
        .options(joinedload(models.Client.created_by))
        .where(models.Client.id == client.get("id"))
    )
    db_client = result.scalars().first()

    assert db_client.name == "test_client", f"Client was created into database with name: {db_client.name} insted of test_client"
    assert db_client.email == "client@test.com", f"Client was created into database with email: {db_client.email} insted of client@test.com"
    assert db_client.id == client.get("id")
    assert db_client.created_by_id == client.get("created_by").get("id")
    assert db_client.created_by.username == client.get("created_by").get("username")
    assert db_client.created_by.image_file == client.get("created_by").get("image_file")

    print(f"== DATABASE CLIENT | ENDPOINT RESPONSE ==\n"
          f"ID: {db_client.id} | {client.get('id')}\n"
          f"Name : {db_client.name} | {client.get('name')}\n"
          f"Email : {db_client.email} | {client.get('email')}\n"
          f"\n=== CREATED_BY  ===\nID : {db_client.created_by_id} | {client.get('created_by').get("id")}\n"
          f"NAME: {db_client.created_by.username} | {client.get("created_by").get("username")}\n"
          f"Image File: {db_client.created_by.image_file} | {client.get("created_by").get("image_file")}")



@pytest.mark.anyio
async def test_fail_create_client(authenticated_client: AsyncClient):


    # 1. Create client without name
    response = await authenticated_client.post("/api/clients",
                                 json={
                                     "email":"client@test.com"
                                 })
    assert response.status_code == 422
    api_response = response.json()
    detail = api_response.get("detail")[0]
    msg = detail.get("msg")
    assert msg == "Field required"


    # 2.Create client without email
    response = await authenticated_client.post("/api/clients",
                                 json={
                                     "name":"test_client"
                                 })
    assert response.status_code == 422
    api_response = response.json()
    detail = api_response.get("detail")[0]
    msg = detail.get("msg")
    assert msg == "Field required"


@pytest.mark.anyio
async def test_get_client(authenticated_client : AsyncClient):
    new_client =  await create_test_client(authenticated_client)
    response = await authenticated_client.get("/api/clients")
    assert response.status_code == 200
    clients : list = response.json()
    assert len(clients) == 1
    assert clients[0].get("name") == new_client.get("name")
    assert clients[0].get("id") == new_client.get("id")
    assert clients[0].get("created_by") == new_client.get("created_by")


@pytest.mark.anyio
async def test_get_user_without_authorization(client: AsyncClient):
    user = await create_test_user(client)
    owner_token = await login_user(client)

    response = await client.post("/api/clients",
                                 json={
                                     "name":"test_user",
                                     "email":"test@client.com"
                                 },
                                 headers=auth_header(owner_token))
    test_client = response.json()
    print(f"TEST CLIENT DATA: {test_client}")

    other_user = await create_test_user(client, username="other_user",email="other@example.com")
    other_user_email = str(other_user.get("email"))
    other_user_token = await login_user(client,email=other_user_email)
    test_client_id = test_client.get("id")
    print(f"TEST_CLIENT_ID : {test_client_id}")
    response = await client.get(f"/api/clients/{test_client_id}",headers=auth_header(other_user_token))
    print(response.text)
    assert response.status_code == 400
    assert "No client with the current id" in response.text























