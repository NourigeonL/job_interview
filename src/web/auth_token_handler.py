from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel
from src.core.features.authentication.interfaces import User
class UserToken(BaseModel):
    id : str

scheme = APIKeyHeader(name="Bearer")

class Tokens(BaseModel):
    access : str

async def verify_token(token : Annotated[str, Depends(scheme)]) -> dict:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    raise credentials_exception

async def generate_tokens(user : User) -> Tokens:
    return Tokens(access=str(user.id))

async def get_current_user_from_token(payload : Annotated[dict, Depends(verify_token)]) -> UserToken:
    return UserToken(id="id")