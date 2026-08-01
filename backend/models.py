from __future__ import annotations
from datetime import UTC, datetime
from pygments.lexers import data
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config import settings
from database import Base
from pgvector.sqlalchemy import Vector

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username : Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email : Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(String(200), nullable=False)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda : datetime.now(tz=UTC)
    )
    created_clients : Mapped[list["Client"]] = relationship(back_populates="created_by", cascade="all, delete-orphan")
    image_file : Mapped[str | None] = mapped_column(String(200),nullable=True,default=None)
    reset_token : Mapped[list[PasswordResetToken]] = relationship(back_populates="user",cascade="all, delete-orphan")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

class Client(Base):
    __tablename__ = "clients"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    email : Mapped[str] = mapped_column(String(120), unique=True)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda : datetime.now(tz=UTC)
    )
    created_by_id : Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    created_by : Mapped["User"] = relationship(back_populates="created_clients")

    documents : Mapped[list["Document"]] = relationship(back_populates="client", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(250),nullable=False)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda : datetime.now(tz=UTC)
    )
    file : Mapped[str | None] = mapped_column(String(200), nullable=False, default=None)
    client_id : Mapped[int] = mapped_column(ForeignKey("clients.id",ondelete="CASCADE"))
    client : Mapped["Client"] = relationship(back_populates="documents")

    @property
    def file_path(self) -> str | None:
        if self.file:
            return f"/documents/{self.file}"
        return None


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text_content : Mapped[str] = mapped_column(Text, nullable=False)
    embedding : Mapped[list[float]] = mapped_column(Vector(1536),nullable=True)
    document_id : Mapped[int] = mapped_column(ForeignKey("documents.id",ondelete="CASCADE"))



class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    token_hash : Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda : datetime.now(tz=UTC)
    )
    user : Mapped[User] = relationship(back_populates="reset_token")

