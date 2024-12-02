#-- stage 1
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /dome_model_api

RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY requirements.txt .

COPY .env.example .env

ARG APP_NAME
ARG APP_SECRET_KEY
ARG API_EXTERNAL_BASE_URL
ARG API_EXTERNAL_PREFIX

RUN echo "APP_NAME=${APP_NAME}" > .env && \
    echo "APP_SECRET_KEY=${APP_SECRET_KEY}" >> .env && \
    echo "API_EXTERNAL_BASE_URL=${API_EXTERNAL_BASE_URL}" >> .env && \
    echo "API_EXTERNAL_PREFIX=${API_EXTERNAL_PREFIX}" >> .env

RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

#-- stage 2
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /dome_model_api

COPY --from=builder /dome_model_api /dome_model_api
COPY --from=builder /opt/venv /opt/venv

EXPOSE 5001

CMD ["gunicorn", "__init__:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:5001"]
