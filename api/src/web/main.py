from fastapi import FastAPI, Depends, WebSocket, BackgroundTasks
from api.src.web.service_locator import service_locator
from api.src.features.authentication.interfaces import UserRegistrationForm, LoginForm
from api.src.features.process.interfaces import RequestForm
from api.src.web.auth_token_handler import Tokens, generate_tokens
from common.config import get_message_broker
from typing import Annotated
from common.message_brokers.interfaces import IMessageBroker, Request
from api.src.web.dependencies import lifespan, get_current_user, UserToken
from fastapi.responses import HTMLResponse

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
async def process_requests(request_form : RequestForm, background_tasks: BackgroundTasks, curren_user : Annotated[UserToken, Depends(get_current_user)]):
    background_tasks.add_task(service_locator.process_service.process_requests, curren_user.id, request_form)

# @app.get("/responses/")
# async def get_reponses(nb_max_response : int, msg_broker : Annotated[IMessageBroker, Depends(get_message_broker)]):
#     return await msg_broker.receive_reponses(nb_max_response)

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")