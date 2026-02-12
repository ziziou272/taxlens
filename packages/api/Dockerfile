FROM python:3.12-slim
WORKDIR /app
COPY packages/engine /app/packages/engine
COPY packages/api /app/packages/api
RUN pip install --no-cache-dir /app/packages/engine /app/packages/api
WORKDIR /app/packages/api
EXPOSE 8100
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8100}
