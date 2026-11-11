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

# F16 (AA5): run as an unprivileged user. It must be able to write the proposal drafts bind
# (TTOD_PROPOSAL_DIR). On a Linux host: `sudo chown -R 10001:10001 data/proposals` once (see the
# Lilith checklist); Docker Desktop on macOS maps ownership itself.
ARG TTOD_UID=10001
RUN useradd --uid "${TTOD_UID}" --user-group --create-home --shell /usr/sbin/nologin ttod \
    && mkdir -p /workspace/services/backend/data/proposals \
    && chown -R ttod:ttod /workspace/services/backend/data
USER ttod

EXPOSE 8000
# --no-access-log: the app writes one JSON line per request with its request id (F48).
CMD ["uvicorn", "services.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

