FROM python:3.12-slim-bullseye

WORKDIR /app
COPY common /app/common
COPY message_brokers /app/message_brokers
COPY storages /app/storages
COPY result_handler/src /app/result_handler/src
COPY result_handler/result_handler_requirements.txt /app
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r result_handler_requirements.txt
CMD ["/opt/venv/bin/python", "-m", "result_handler.src.main"]