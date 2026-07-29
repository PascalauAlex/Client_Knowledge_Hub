from datetime import timedelta
from typing import Annotated
from PIL import UnidentifiedImageError
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
import models
from utils.auth import (
    CurrentUser,
    create_access_token,
    hash_password,
    verify_password,
    hash_reset_token, generate_token,
)
from config import settings
from database import get_db
from utils.email_utils import send_password_reset_email
from schemas import (
    UserPublic,
    UserPrivate,
    UserCreate, Token, ChangePasswordRequest, ResetPasswordRequest, ForgotPasswordRequest
)
from sqlalchemy import delete as sql_delete
from datetime import UTC, datetime
from utils.image_utils import process_profile_image, delete_profile_image_s3, upload_profile_image_s3, create_presigned_url

router = APIRouter()

@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.username) == user.username.lower(),
        ),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = await db.execute(
        select(models.User).where(func.lower(models.User.email) == user.email.lower()),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = models.User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data : Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    # Look up user by email
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email

    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower(),
        ),
    )

    user = result.scalars().first()

    # Verify user exists and password is correct

    # Don't revel which one failed
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub":str(user.id)},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token,token_type="bearer")

@router.get(path="/me",response_model=UserPrivate)
async def get_current_user(current_user : CurrentUser):
    image_name = current_user.image_file
    image_path = create_presigned_url(object_name=f"files/{image_name}")
    current_user.image_file = image_path
    return current_user

@router.get(path="/{user_id}",response_model=UserPublic)
async def get_user(user_id : int,
                   db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))

    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@router.post(path="/me/password", status_code=status.HTTP_200_OK)
async def change_password(password_data : ChangePasswordRequest,
                          current_user: CurrentUser,
                          db: Annotated[AsyncSession, Depends(get_db)]):
    if not verify_password(password_data.current_password,current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password doesn't match"
        )

    current_user.password_hash = hash_password(password_data.new_password)

    await db.execute(
        sql_delete(models.PasswordResetToken)
        .where(models.PasswordResetToken.user_id == current_user.id))


    await db.commit()
    return {"message":"Password was changed successfully!"}



@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token_hash = hash_reset_token(request_data.token)

    result = await db.execute(
        select(models.PasswordResetToken).where(
            models.PasswordResetToken.token_hash == token_hash,
        ),
    )
    reset_token = result.scalars().first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if reset_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        await db.delete(reset_token)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    result = await db.execute(
        select(models.User).where(models.User.id == reset_token.user_id),
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user.password_hash = hash_password(request_data.new_password)

    await db.execute(
        sql_delete(models.PasswordResetToken).where(
            models.PasswordResetToken.user_id == user.id,
        ),
    )

    await db.commit()
    return {
        "message": "Password reset successfully. You can now log in with your new password.",
    }



@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == request_data.email.lower(),
        ),
    )
    user = result.scalars().first()

    if user:
        await db.execute(
            sql_delete(models.PasswordResetToken).where(
                models.PasswordResetToken.user_id == user.id,
            ),
        )

        token = generate_token()
        token_hash = hash_reset_token(token)
        expires_at = datetime.now(UTC) + timedelta(
            minutes=settings.reset_token_expire_minutes,
        )

        reset_token = models.PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(reset_token)
        await db.commit()

        background_tasks.add_task(
            send_password_reset_email,
            to_email=user.email,
            username=user.username,
            token=token,
        )

    return {
        "message": "If an account exists with this email, you will receive password reset instructions.",
    }


@router.post(path="/upload_profile_picture",status_code=status.HTTP_200_OK, response_model=UserPublic)
async def upload_profile_picture(file: UploadFile, user_id:int , db: Annotated[AsyncSession, Depends(get_db)], current_user : CurrentUser):

    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not authorized to update this user.")

    content = await file.read()

    if len(content) > settings.max_image_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The maximum image size must be lower than 5MB."
        )

    try:
        processed_bytes ,new_file_name = await run_in_threadpool(process_profile_image,content)
    except UnidentifiedImageError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP)."
        )
    #Upload to S3 (also run in thread pool, via wrapper)
    try:
        await upload_profile_image_s3(processed_bytes, new_file_name)
    except ClientError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image. AWS Error",
        ) from err

    old_file = current_user.image_file

    current_user.image_file = new_file_name

    await db.commit()
    await db.refresh(current_user)

    if old_file:
        await delete_profile_image_s3(old_file)
    return current_user


@router.delete("/delete_profile_picture", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def delete_profile_picture(user_id : int ,
                                 db: Annotated[AsyncSession, Depends(get_db)],
                                 current_user: CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorized to modify this user"
        )

    old_filename = current_user.image_file

    if old_filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile picture to delete"
        )

    current_user.image_file = None
    await db.commit()
    await db.refresh(current_user)

    await delete_profile_image_s3(old_filename)

    return current_user

@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user(current_user: CurrentUser,
                      user_id:int,
                      db:Annotated[AsyncSession, Depends(get_db)]
)->dict[str,str]:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    profile_pic = current_user.image_file
    await db.execute(sql_delete(models.User).where(models.User.id == user_id))

    await db.commit()

    if profile_pic:
        await delete_profile_image_s3(profile_pic)

    return {"message":"User was deleted successfully"}


















































