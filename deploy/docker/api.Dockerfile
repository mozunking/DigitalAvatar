FROM python:3.11-slim
WORKDIR /app
COPY apps/api /app
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .[dev]
# Create data and logs directories
RUN mkdir -p /app/data /app/logs
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
