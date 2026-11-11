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

# F16 (AA5): unprivileged user (it reads ttod.yml and talks to Ollama; it writes nothing but a home).
ARG TTOD_UID=10001
ARG TTOD_GID=10001
RUN (getent group "${TTOD_GID}" >/dev/null || groupadd --gid "${TTOD_GID}" ttod) \
    && (getent passwd "${TTOD_UID}" >/dev/null || useradd --uid "${TTOD_UID}" --gid "${TTOD_GID}" --no-create-home --shell /usr/sbin/nologin ttod) \
    && mkdir -p /home/ttod && chown "${TTOD_UID}:${TTOD_GID}" /home/ttod
ENV HOME=/home/ttod
USER ${TTOD_UID}:${TTOD_GID}

EXPOSE 3001
CMD ["python", "services/mcp/server.py"]

