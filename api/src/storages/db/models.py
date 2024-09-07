from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, SQLModel
import uuid as uuid_pkg
from sqlalchemy import text
from datetime import datetime

class UUIDModel(SQLModel):
   id: uuid_pkg.UUID = Field(
       default_factory=uuid_pkg.uuid4,
       primary_key=True,
       index=True,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("gen_random_uuid()"),
           "unique": True
       }
   )

class TimestampModel(SQLModel):
   created_at: datetime = Field(
       default_factory=datetime.utcnow,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("current_timestamp(0)")
       }
   )

   updated_at: datetime = Field(
       default_factory=datetime.utcnow,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("current_timestamp(0)"),
           "onupdate": text("current_timestamp(0)")
       }
   )

class UserBase(SQLModel):
    username : str = Field(unique=True)
    hashed_password: str
    
class User(UUIDModel,UserBase, table=True):
    __tablename__ = "users"
    
class UserRead(UserBase, UUIDModel):
    pass

class UserCreate(UserBase):
    pass

class RequestBase(SQLModel):

    user_id : uuid_pkg.UUID = Field(default=None, foreign_key="users.id")
    input : str
    output : str

class Request(UUIDModel,RequestBase,TimestampModel, table=True):
    __tablename__ = "requests"

class RequestRead(RequestBase, UUIDModel):
    pass

class RequestCreate(RequestBase):
    pass