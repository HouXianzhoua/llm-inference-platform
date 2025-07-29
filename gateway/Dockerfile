# gateway/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway .
COPY scripts /app/scripts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "--port", "8000"]
