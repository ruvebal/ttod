FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app
COPY services/mcp/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY ttod_core ./ttod_core
COPY ttod.yml ./ttod.yml
COPY services/mcp ./services/mcp

EXPOSE 3001
CMD ["python", "services/mcp/server.py"]

