import uuid
from httpx import AsyncClient
from pathlib import Path
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
from models import PasswordResetToken
from routers.users import reset_password
from tests.conftest import auth_header, create_test_user, login_user
from unittest.mock import AsyncMock, patch
from utils.auth import hash_reset_token
from datetime import datetime, timedelta


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username":"testuser"
        }
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_creating_user_success(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        url="/api/users",
        json={
         "username": "testuser",
         "email": "user@example.com",
         "password": "securepassword123"
       }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "image_file" in data
    assert "password" not in data
    assert "password_hash" not in data

    result = await db_session.execute(select(models.User).where(models.User.id == data['id']))
    user = result.scalars().first()

    assert user.username == data["username"]
    assert user.email == data["email"]
    assert user.id == data["id"]
    assert user.image_file == data["image_file"]



@pytest.mark.anyio
async def test_get_user_me(client: AsyncClient):
    user = await create_test_user(client)
    assert user

    token = await login_user(client,"test@example.com", "testpassword123")

    assert token
    authorization = auth_header(token)

    response = await client.get(
        url="/api/users/me",
        headers=authorization
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == user["username"]
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "password_hash" not in data
    assert "id" in data
    assert "image_file" in data

@pytest.mark.anyio
async def test_change_password(client:AsyncClient):
    user = await create_test_user(client)

    assert user

    token = await login_user(client, "test@example.com", "testpassword123")

    response = await client.post(
        "/api/users/me/password",
        json={
        "current_password":"testpassword123",
        "new_password":"123testpassword"
        },
        headers=auth_header(token)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Password was changed successfully!"
    assert "password" not in data
    assert "current_password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_reset_password(client: AsyncClient, db_session: AsyncSession):
    user = await create_test_user(client)

    raw_token = str(uuid.uuid4())
    hashed_token = hash_reset_token(raw_token)

    password_reset_token = PasswordResetToken(
        user_id=user["id"],
        token_hash=hashed_token,
        expires_at= datetime.now() + timedelta(minutes=30)
    )

    db_session.add(password_reset_token)
    await db_session.commit()

    response = await client.post(
        "/api/users/reset-password",
        json={
            "token":raw_token,
            "new_password":"123testpassword"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Password reset successfully. You can now log in with your new password."

@pytest.mark.anyio
async def test_delete_user(client: AsyncClient, db_session: AsyncSession):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
        f"/api/users/delete?user_id={user['id']}",
        headers=auth_header(token)
    )

    assert response.status_code == 200, f"{response.text}"
    data = response.json()
    assert data['message'] == 'User was deleted successfully'

    result = await db_session.execute(select(models.User).where(models.User.id == user['id']))
    check_for_user = result.scalars().first()

    assert check_for_user is None


@pytest.mark.anyio
async def test_upload_profile_picture(client: AsyncClient):
    pass



















