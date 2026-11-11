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

**Orphan files (F31, Phase AA5).** A draft is written to disk first, then indexed in Redis. If Redis fails
between the two steps, the API answers 503 and the file stays here with no Redis entry: an *orphan* that
the web reviewer queue never shows. It is harmless (no student sees it as accepted) but worth sweeping
now and then. A file whose id is missing from the queue is an orphan:

```bash
ls data/proposals/*.json                                   # disk
docker compose exec redis redis-cli --scan --pattern 'ttod:proposal:*' | head   # Redis index
```

Import it with `cli.py proposal import` if it is worth reviewing, or delete it.
