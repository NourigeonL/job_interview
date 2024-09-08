FROM python:3.12-slim-bullseye

WORKDIR /app
COPY common /app/common
COPY message_brokers /app/message_brokers
COPY ai/src /app/ai/src
COPY ai/ai_requirements.txt /app
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r ai_requirements.txt
CMD ["/opt/venv/bin/python", "-m", "ai.src.main"]