# monitoring/gpu-monitor.Dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pynvml statsd

COPY monitoring/gpu_monitor.py /app/gpu_monitor.py

WORKDIR /app

CMD ["python", "gpu_monitor.py"]
