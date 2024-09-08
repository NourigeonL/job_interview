from sqlmodel import Field, SQLModel, Relationship
import uuid as uuid_pkg
from sqlalchemy import text
from datetime import datetime
from common.enums import RequestStatus

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


class RequestBase(SQLModel):
    job_id: uuid_pkg.UUID = Field(foreign_key="jobs.id")
    user_id : uuid_pkg.UUID = Field(index=True)
    input : str
    output : str | None = None
    status : str = RequestStatus.PENDING.value

class Request(UUIDModel,RequestBase,TimestampModel, table=True):
    __tablename__ = "requests"
    job: "Job" = Relationship(back_populates="requests")


class JobBase(SQLModel):
    user_id : uuid_pkg.UUID = Field(index=True)
    

class Job(UUIDModel,JobBase,TimestampModel, table=True):
    __tablename__ = "jobs"
    requests : list["Request"]= Relationship(back_populates="job")

class RequestPatch(SQLModel):
    input : str | None = None
    output : str | None = None

class UserBase(SQLModel):
    username : str = Field(unique=True)
    hashed_password: str
    
class User(UUIDModel,UserBase, table=True):
    __tablename__ = "users"
    