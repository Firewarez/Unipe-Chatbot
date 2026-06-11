FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY services/notificacoes/notificacoes_service ./notificacoes_service

EXPOSE 8000
CMD ["uvicorn", "notificacoes_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

