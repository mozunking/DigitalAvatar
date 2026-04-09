FROM python:3.11-slim
WORKDIR /app
COPY apps/api /app
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .[dev]
CMD ["python", "-m", "app.worker"]
