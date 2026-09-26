import re
from dataclasses import dataclass
from datetime import datetime
from io import RawIOBase
from typing import Literal, Optional, Annotated
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, AfterValidator


# * VALIDATORS * #
def validate_password(v: str)->str:
    if len(v) < 8:
        raise ValueError("Password must have at least 8 characters")
    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain a lower case letter.")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain an upper case letter.")
    if not re.search(r"\d", v):
        raise ValueError("Password must contain a digit.")
    if not re.search(r"[^A-Za-z0-9]", v):
        raise ValueError("Password must contain a special character")
    return v


# ** USER SCHEMAS ** #

Password = Annotated[str, Field(min_length=8, max_length=50), AfterValidator(validate_password)]

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: Password


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(gt=0)
    username: str
    image_file: Optional[str]


class UserPrivate(UserPublic):
    email: EmailStr
    created_at: datetime


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(default=None, max_length=120)


# * AUTH SCHEMAS * #

class Token(BaseModel):
    access_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: Password


class ChangePasswordRequest(BaseModel):
    current_password: Password
    new_password: Password


# * CLIENT SCHEMA * #

class ClientBase(BaseModel):
    name: str = Field(min_length=3, max_length=150)

class ClientCreate(ClientBase):
    email: EmailStr = Field(max_length=120)

class ClientResponse(ClientBase):
    id: int = Field(gt=0)
    email: EmailStr
    created_by: UserPublic

    model_config = ConfigDict(from_attributes=True)

class ClientUpdate(BaseModel):
    email: Optional[EmailStr]
    name : Optional[str]



# * DOCUMENT SCHEMA * #

class DocumentBase(BaseModel):
    name: str = Field(min_length=3, max_length=250)


class DocumentResponse(DocumentBase):
    id : int = Field(gt=0)
    file: str
    client_id: int
    type: Literal["invoice","contract","report"]
    extension_type: str
    created_at: datetime


class DocumentSummaryResponse(BaseModel):
    summary : dict = Field(title="Document Summary",description="Structured document summary provided by LLamaCloud")


class DocumentChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_id: int
    document: DocumentResponse
    client_id: int
    chunk_index: int
    page: Optional[int]
    text: str

# * CHAT SCHEMA * #

class LLMResponse(DocumentResponse):
    source: str
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
    url: Optional[str]


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)

