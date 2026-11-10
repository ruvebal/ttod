# Proposal drafts (host bind mount)

The backend writes proposal drafts here: the disk half of the Redis dual-write. Compose mounts this
folder at `TTOD_PROPOSAL_DIR` inside the container (F25, Phase AA5 lane A), so the drafts survive
`make rebuild` and a backend recreate, and the instructor can read them from the host.

**Accepting a web draft.** `cli.py proposal accept` reads the repository's `proposals/` store, not
this folder, so import the draft first:

```bash
.venv/bin/python cli.py proposal import data/proposals/<id>.json   # copies it into proposals/
.venv/bin/python cli.py proposal review <id> …                      # then accept as usual
```

The Redis copy keeps status `proposed`, so the draft stays in the web reviewer queue until it is
resolved there.

Contents are gitignored: drafts are user input, not corpus. Back the folder up with `data/redis/`.
Override the host path with `TTOD_PROPOSAL_HOST_DIR` in `.env`.
