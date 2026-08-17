from datetime import datetime, UTC

from pydantic import BaseModel, Field, EmailStr, SecretStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    image_file : str



class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)



class Token(BaseModel):
    access_token: str
    token_type: str



class ClientBase(BaseModel):
    name : str = Field(min_length=3, max_length=150)

class ClientCreate(ClientBase):
    email: EmailStr = Field(max_length=120)

class ClientResponse(ClientBase):
    id : int
    email : EmailStr
    created_by : UserPublic


    model_config = ConfigDict(from_attributes=True)


class ClientUpdate(ClientBase):
    email : EmailStr = Field(default=None, max_length=120)




class DocumentBase(BaseModel):
    name: str = Field(min_length=3, max_length=250)

class DocumentCreate(DocumentBase):
    file : str = Field(max_length=200)
    client_id : int

class DocumentResponse(DocumentBase):
    id: int
    file: str
    client_id : int
    created_at : datetime
    extension_type : str

    


class TagBase(BaseModel):
    pass



class ForgotPasswordRequest(BaseModel):
    email : EmailStr = Field(max_length=120)

class ResetPasswordRequest(BaseModel):
    token : str
    new_password : str

class ChangePasswordRequest(BaseModel):
    current_password : str
    new_password : str = Field(min_length=8)





























