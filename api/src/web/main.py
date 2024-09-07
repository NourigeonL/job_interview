from fastapi import FastAPI
from api.src.web.service_locator import service_locator
from api.src.features.authentication.interfaces import UserRegistrationForm, LoginForm
from api.src.web.auth_token_handler import Tokens, generate_tokens
from pydantic import BaseModel


app = FastAPI()

@app.post("/login/")
async def log_in(login_form : LoginForm) -> Tokens:
    user = await service_locator.authentication_service.log_in_user(login_form)
    return await generate_tokens(user)
    
@app.post("/register/")
async def register(user_registration : UserRegistrationForm) -> Tokens:
    user = await service_locator.authentication_service.register_user(user_registration)
    return await generate_tokens(user)

@app.get("/")
async def hello_world():
    return {"Hello":"world"}