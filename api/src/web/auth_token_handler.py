from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel
from api.src.features.authentication.interfaces import UserDto
from common.config import settings
from jose import jwt, JWTError

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
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        raise credentials_exception

async def generate_tokens(user : UserDto) -> Tokens:
    encoded_jwt = jwt.encode({"user_id": str(user.id)}, settings.JWT_SECRET, algorithm="HS256")
    return Tokens(access=encoded_jwt)

async def get_current_user_from_token(payload : Annotated[dict, Depends(verify_token)]) -> UserToken:
    return UserToken(id=payload["user_id"])