FROM python:3.12-slim-bullseye

WORKDIR /app
COPY common /app/common
COPY api/src /app/api/src
COPY api/api_requirements.txt /app
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r api_requirements.txt
CMD ["/opt/venv/bin/uvicorn", "api.src.web.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]