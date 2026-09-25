from datetime import datetime
from typing import Literal, Annotated
from pydantic import BaseModel, Field, EmailStr, ConfigDict

import models


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=50)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    image_file: str | None


class UserPrivate(UserPublic):
    email: EmailStr
    created_at: datetime


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class Token(BaseModel):
    access_token: str
    token_type: str


class ClientBase(BaseModel):
    name: str = Field(min_length=3, max_length=150)


class ClientCreate(ClientBase):
    email: EmailStr = Field(max_length=120)


class ClientResponse(ClientBase):
    id: int
    email: EmailStr
    created_by: UserPublic

    model_config = ConfigDict(from_attributes=True)


class ClientUpdate(ClientBase):
    email: EmailStr = Field(max_length=120)


class DocumentBase(BaseModel):
    name: str = Field(min_length=3, max_length=250)


class DocumentResponse(DocumentBase):
    id : int
    file: str
    client_id: int
    type: str
    extension_type: str
    created_at: datetime


class DocumentSummaryResponse(BaseModel):
    summary : dict = Field(default={"summary":""})

class LLMResponse(DocumentResponse):
    source: str
    text: str


class DocumentChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_id: int
    document: DocumentResponse
    client_id: int
    chunk_index: int
    page: int | None
    text: str


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


class ChatSource(BaseModel):
    id: int
    title: str
    url: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
