# Proposal drafts (host bind mount)

The backend writes proposal drafts here: the disk half of the Redis dual-write. Compose mounts this
folder at `TTOD_PROPOSAL_DIR` inside the container (F25, Phase AA5 lane A), so the drafts survive
`make rebuild` and a backend recreate, and the instructor can review them from the host with
`cli.py proposal …`.

Contents are gitignored: drafts are user input, not corpus. Back the folder up with `data/redis/`.
Override the host path with `TTOD_PROPOSAL_HOST_DIR` in `.env`.
