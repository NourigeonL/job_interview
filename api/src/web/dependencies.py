from fastapi import Depends
from .auth_token_handler import get_current_user_from_token, UserToken
from typing import Annotated

async def get_current_user(user_token : Annotated[UserToken, Depends(get_current_user_from_token)]) -> UserToken:
    return user_token