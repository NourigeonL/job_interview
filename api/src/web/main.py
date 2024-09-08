from fastapi import FastAPI, Depends
from api.src.web.service_locator import service_locator
from api.src.features.authentication.interfaces import UserRegistrationForm, LoginForm
from api.src.web.auth_token_handler import Tokens, generate_tokens
from common.config import settings
from typing import Annotated
from api.src.web.dependencies import lifespan, get_current_user, UserToken, exception_handler
from common.storages.db.models import RequestPatch
from common.exceptions import GenericError
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class RequestForm(BaseModel):
    requests : list[str] = Field(..., max_length=settings.BATCH_SIZE)
    
    @field_validator('requests')
    @classmethod
    def validate_requests(cls, v: list[str]) -> list[str]:
        if len(v) > settings.MAX_NB_REQUESTS:
            raise ValueError(f'The requests list can have a maximum of {settings.MAX_NB_REQUESTS} items')
        
        for item in v:
            if not 1 <= len(item) <= settings.MAX_NB_CHARACTERS_IN_REQUEST:
                raise ValueError(f'Each request must be between 1 and {settings.MAX_NB_CHARACTERS_IN_REQUEST} characters long (got {len(item)} characters long string)')
        
        return v


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(GenericError, exception_handler)

@app.post("/login/")
async def log_in(login_form : LoginForm) -> Tokens:
    user = await service_locator.authentication_service.log_in_user(login_form)
    return await generate_tokens(user)
    
@app.post("/register/")
async def register(user_registration : UserRegistrationForm) -> Tokens:
    user = await service_locator.authentication_service.register_user(user_registration)
    return await generate_tokens(user)

@app.post("/process/")
async def process_requests(request_form : RequestForm, current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.request_service.send_requests(current_user.id, request_form.requests)

@app.get("/requests/{request_id}")
async def get_request(request_id : UUID, current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.crud_request.get(current_user.id, request_id)

@app.get("/requests")
async def get_all_requests(current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.crud_request.get_all(current_user.id)

@app.patch("/requests/{request_id}")
async def patch_request(request_id : UUID, data : RequestPatch, current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.crud_request.patch(current_user.id, request_id, data)

@app.delete("/requests/{request_id}")
async def delete_request(request_id : UUID, current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.crud_request.delete(current_user.id, request_id)

@app.get("/jobs/{job_id}")
async def get_job_info(job_id : UUID, current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.crud_request.get_job_info(current_user.id, job_id)

@app.get("/jobs")
async def get_jobs_summary( current_user : Annotated[UserToken, Depends(get_current_user)]):
    return await service_locator.crud_request.get_jobs_summary(current_user.id)