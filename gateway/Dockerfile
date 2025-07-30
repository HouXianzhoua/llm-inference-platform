# gateway/Dockerfile
FROM python:3.10-slim

# 安装 netcat 工具（用于发送 StatsD 指标调试）
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway .
COPY scripts /app/scripts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
