FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace

WORKDIR /workspace
COPY services/backend/requirements.txt /tmp/backend-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt
COPY ttod_core ./ttod_core
COPY schema ./schema
COPY ttod.yml ./ttod.yml
COPY services/backend ./services/backend

# F16 (AA5): run as an unprivileged user. `make` builds it with your host uid/gid (TTOD_UID/TTOD_GID),
# so the proposal drafts bind (TTOD_PROPOSAL_DIR) is writable without any chown; plain `docker compose`
# uses 10001. Numeric USER, so a uid or gid the base image already has still works.
ARG TTOD_UID=10001
ARG TTOD_GID=10001
RUN (getent group "${TTOD_GID}" >/dev/null || groupadd --gid "${TTOD_GID}" ttod) \
    && (getent passwd "${TTOD_UID}" >/dev/null || useradd --uid "${TTOD_UID}" --gid "${TTOD_GID}" --no-create-home --shell /usr/sbin/nologin ttod) \
    && mkdir -p /home/ttod /workspace/services/backend/data/proposals \
    && chown -R "${TTOD_UID}:${TTOD_GID}" /home/ttod /workspace/services/backend/data
ENV HOME=/home/ttod
USER ${TTOD_UID}:${TTOD_GID}

EXPOSE 8000
# --no-access-log: the app writes one JSON line per request with its request id (F48).
CMD ["uvicorn", "services.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

