from fastapi import FastAPI, Depends, WebSocket, BackgroundTasks, Query
from api.src.web.service_locator import service_locator
from api.src.features.authentication.interfaces import UserRegistrationForm, LoginForm
from api.src.web.auth_token_handler import Tokens, generate_tokens
from common.config import settings
from typing import Annotated
from common.message_brokers.interfaces import IMessageBroker, Request
from api.src.web.dependencies import lifespan, get_current_user, UserToken
from fastapi.responses import HTMLResponse
from api.src.storages.db.models import RequestRead, RequestPatch
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ValidationInfo

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

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.post("/login/")
async def log_in(login_form : LoginForm) -> Tokens:
    user = await service_locator.authentication_service.log_in_user(login_form)
    return await generate_tokens(user)
    
@app.post("/register/")
async def register(user_registration : UserRegistrationForm) -> Tokens:
    user = await service_locator.authentication_service.register_user(user_registration)
    return await generate_tokens(user)

@app.post("/process/")
async def process_requests(request_form : RequestForm, background_tasks: BackgroundTasks, current_user : Annotated[UserToken, Depends(get_current_user)]):
    background_tasks.add_task(service_locator.process_service.process_requests, current_user.id, request_form)

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

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")