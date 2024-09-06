FROM python:3.12-slim-bullseye

COPY ./src /app/src
WORKDIR /app
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r ./src/requirements.txt
CMD ["/opt/venv/bin/uvicorn", "src.web.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]