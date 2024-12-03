#-- stage 1
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /system_backup

RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY requirements.txt .

# COPY .env.example .env

RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

#-- stage 2
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /system_backup

COPY --from=builder /system_backup /system_backup
COPY --from=builder /opt/venv /opt/venv

EXPOSE 5001

CMD ["gunicorn", "__init__:app", "-w", "4", "-k", "gevent", "-b", "0.0.0.0:5000"]