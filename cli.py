#!/usr/bin/env python3
"""
TTOD CLI — 道 The Tao of Development (TTOD)

All ttod.yml mutations go through TTODRepository write transactions.
Read docs/DEV_PLAN/PHASES/Q3-atomic-repository-cli.md before changing write paths.
"""

from __future__ import annotations

import json
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import typer
import yaml

from ttod_core.canonical import Canonicalizer
from ttod_core.exporter import Exporter
from ttod_core.bridge import BridgeError, TTODBridge, TEST_REVIEWER_ID
from ttod_core.migration import migrate_root, serialize_migrated_document, write_candidate
from ttod_core.proposals import create_proposal
from ttod_core.repository import ProposalStore, RepositoryError, TTODRepository
from ttod_core.translation import (
    OLLAMA_DEFAULT_HOST,
    TranslationError,
    build_translation_candidate,
    find_active_translations,
    translate_quote,
)
from ttod_core.validation import TTODValidator

app = typer.Typer(help="道 The Tao of Development (TTOD) — pedagogical wisdom CLI")
proposal_app = typer.Typer(help="Proposal lifecycle (only accept touches ttod.yml)")
bridge_app = typer.Typer(help="Athanor bridge transport (serialization only; no canonical writes)")
app.add_typer(proposal_app, name="proposal")
migrate_app = typer.Typer(help="Phase Q6 v2→v3 migration (live ttod.yml only with --apply)")
app.add_typer(migrate_app, name="migrate")

DEFAULT_TTOD = Path(__file__).parent / "ttod.yml"
DEFAULT_EXPORTS = Path(__file__).parent / "exports"
DEFAULT_PROPOSALS = Path(__file__).parent / "proposals"

VALID_LEVELS = {"beginner", "intermediate", "advanced", "master"}


def _repo(file: Optional[Path]) -> TTODRepository:
    return TTODRepository(file or DEFAULT_TTOD)


def _proposal_store() -> ProposalStore:
    return ProposalStore(DEFAULT_PROPOSALS)


def _status(quote: dict[str, Any]) -> str:
    return str(quote.get("status") or "active")


def _translation_targets(candidate: dict[str, Any], target_lang: str) -> set[str]:
    if candidate.get("lang") != target_lang:
        return set()
    targets: set[str] = set()
    for edge in candidate.get("relation_edges") or []:
        if (
            isinstance(edge, dict)
            and edge.get("relation_type") == "translation_of"
            and edge.get("target")
        ):
            targets.add(str(edge["target"]))
    return targets


def _pending_translation_sources(target_lang: str) -> dict[str, list[str]]:
    by_source: dict[str, list[str]] = {}
    if not DEFAULT_PROPOSALS.exists():
        return by_source
    for path in sorted(DEFAULT_PROPOSALS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("status") not in {"proposed", "needs_revision"}:
            continue
        candidate = data.get("candidate_content") or {}
        if not isinstance(candidate, dict):
            continue
        for source_id in _translation_targets(candidate, target_lang):
            by_source.setdefault(source_id, []).append(str(data.get("proposal_id") or path.stem))
    return by_source


def _eligible_translation_sources(root: dict[str, Any], target_lang: str) -> list[dict[str, Any]]:
    quotes = root.get("quotes", [])
    pending = _pending_translation_sources(target_lang)
    eligible: list[dict[str, Any]] = []
    for quote in quotes:
        if not isinstance(quote, dict):
            continue
        quote_id = quote.get("id")
        if not quote_id:
            continue
        if quote.get("lang") != "en":
            continue
        if _status(quote) != "active":
            continue
        if any(
            isinstance(edge, dict) and edge.get("relation_type") == "translation_of"
            for edge in quote.get("relation_edges") or []
        ):
            continue
        rights = quote.get("rights") or {}
        if rights.get("access") not in (None, "public"):
            continue
        if find_active_translations(quotes, str(quote_id), target_lang):
            continue
        if str(quote_id) in pending:
            continue
        eligible.append(quote)
    return eligible


@app.command()
def validate(
    strict: bool = typer.Option(False, "--strict", help="Treat drift as hard failure"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON diagnostics"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML path (default: ttod.yml)"),
):
    """Validate ttod.yml via Q2V."""
    result = _repo(file).validate(strict=strict)
    if as_json:
        typer.echo(json.dumps(result.to_dict(), indent=2))
    else:
        typer.echo(
            f"{'OK' if result.is_valid else 'FAIL'} — "
            f"{len(result.errors)} errors, {len(result.warnings)} warnings"
        )
        for diag in result.errors[:20]:
            loc = f" [{diag.quote_id}]" if diag.quote_id else ""
            typer.echo(f"  ERROR {diag.code.value}{loc}: {diag.message}")
        for diag in result.warnings[:10]:
            loc = f" [{diag.quote_id}]" if diag.quote_id else ""
            typer.echo(f"  WARN  {diag.code.value}{loc}: {diag.message}")

    if not result.is_valid:
        raise typer.Exit(1)


@app.command()
def stats(
    check: bool = typer.Option(False, "--check", help="Recompute derived metadata and report drift"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML path"),
):
    """Show statistics; --check recomputes derived meta without hand-patching."""
    repo = _repo(file)
    root = repo.load()
    quotes = root.get("quotes", [])

    if check:
        result = repo.stats_check()
        if result.contract_blockers:
            typer.echo("CONTRACT BLOCKER — cannot recompute atomically:")
            for blocker in result.contract_blockers:
                typer.echo(f"  - {blocker}")
            raise typer.Exit(2)

        derived = result.derived
        typer.echo(f"Recomputed total_quotes: {derived.total_quotes}")
        typer.echo(f"Recomputed last_id_by_section: {derived.last_id_by_section}")
        if result.drifts:
            typer.echo(f"\nDRIFT — {len(result.drifts)} field(s) differ from stored meta:")
            for drift in result.drifts:
                typer.echo(f"  {drift.field}: stored={drift.stored!r} computed={drift.computed!r}")
            raise typer.Exit(1)
        typer.echo("\nOK — stored meta matches recomputed snapshot.")
        return

    typer.echo(f"Total quotes: {len(quotes)}\n")

    typer.echo("By section:")
    section_counts: dict[str, int] = {}
    for q in quotes:
        sec = q.get("section")
        if sec:
            section_counts[sec] = section_counts.get(sec, 0) + 1
    for section, count in sorted(section_counts.items(), key=lambda x: -x[1]):
        typer.echo(f"  {section}: {count}")

    typer.echo("\nBy level:")
    level_counts: dict[str, int] = {}
    for q in quotes:
        lvl = q.get("level")
        if lvl:
            level_counts[lvl] = level_counts.get(lvl, 0) + 1
    for level, count in sorted(level_counts.items(), key=lambda x: -x[1]):
        typer.echo(f"  {level}: {count}")

    typer.echo("\nBy origin (missing origin reported explicitly, never defaulted to human):")
    origin_counts: dict[str, int] = {}
    missing_origin = 0
    for q in quotes:
        origin = q.get("origin")
        if origin is None:
            missing_origin += 1
            origin_counts["<missing>"] = origin_counts.get("<missing>", 0) + 1
        else:
            origin_counts[origin] = origin_counts.get(origin, 0) + 1
    for origin, count in sorted(origin_counts.items(), key=lambda x: -x[1]):
        typer.echo(f"  {origin}: {count}")
    if missing_origin:
        typer.echo(f"  ({missing_origin} quotes lack origin — not counted as human)")

    typer.echo("\nBy language (derived from quote lang; never hardcoded):")
    language_counts: dict[str, int] = {}
    missing_lang = 0
    for q in quotes:
        lang = q.get("lang")
        if lang is None:
            missing_lang += 1
            language_counts["<missing>"] = language_counts.get("<missing>", 0) + 1
        else:
            language_counts[lang] = language_counts.get(lang, 0) + 1
    for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):
        typer.echo(f"  {lang}: {count}")
    if missing_lang:
        typer.echo(f"  ({missing_lang} quotes lack lang — migrate via Phase S S2′)")


@app.command()
def snapshot(
    output: Path = typer.Option(..., "--output", help="Output JSON path"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML source"),
):
    """Export a canonical C14N snapshot via Q2E."""
    root = _repo(file).load()
    exporter = Exporter(Canonicalizer())
    manifest = exporter.export_json(root, output)
    typer.echo(f"Snapshot written: {output} (records={manifest.record_count})")


@app.command()
def export(
    format: str = typer.Option("json", help="Export format: json, graph"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output file path"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML source"),
):
    """Export TTOD to canonical JSON or graph projection via Q2E."""
    root = _repo(file).load()
    exporter = Exporter(Canonicalizer())
    DEFAULT_EXPORTS.mkdir(exist_ok=True)

    if format == "json":
        out_path = output or DEFAULT_EXPORTS / "ttod.json"
        manifest = exporter.export_json(root, out_path)
        typer.echo(f"Exported JSON: {out_path} (records={manifest.record_count})")
    elif format == "graph":
        out_path = output or DEFAULT_EXPORTS / "graph.json"
        manifest = exporter.export_graph(root, out_path)
        typer.echo(f"Exported graph: {out_path} (records={manifest.record_count})")
    else:
        typer.echo(f"Unknown format: {format}. Use json or graph.")
        raise typer.Exit(1)


@proposal_app.command("create")
def proposal_create(
    section: str = typer.Option(..., help="Section ID"),
    level: str = typer.Option("intermediate", help="Level"),
    text: str = typer.Option(..., help="Quote text"),
    origin: str = typer.Option("studio", help="Origin: human/studio/blackbox"),
    tags: str = typer.Option("", help="Comma-separated tags"),
    proposer_id: str = typer.Option("cli-user", help="Proposer identifier"),
    output: Optional[Path] = typer.Option(None, "--output", help="Write proposal JSON here"),
):
    """Create a proposal (does not touch ttod.yml)."""
    if level not in VALID_LEVELS:
        typer.echo(f"Invalid level: {level}")
        raise typer.Exit(1)

    candidate: dict[str, Any] = {
        "text": text,
        "section": section,
        "level": level,
        "origin": origin,
    }
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if tag_list:
        candidate["tags"] = tag_list

    proposal = create_proposal(
        candidate_content=candidate,
        proposer_kind="human",
        proposer_id=proposer_id,
        generation_method="cli-proposal-create",
    )

    if output:
        path = _proposal_store().save(proposal)
        typer.echo(f"Proposal saved: {path}")
    else:
        typer.echo(json.dumps(proposal.to_dict(), indent=2))

    typer.echo(f"proposal_id={proposal.proposal_id}")


@proposal_app.command("import")
def proposal_import(
    path: Path = typer.Argument(..., help="Proposal JSON file to import into store"),
):
    """Import a proposal JSON file into the proposals store."""
    store = _proposal_store()
    proposal = store.load_path(path)
    saved = store.save(proposal)
    typer.echo(f"Imported proposal {proposal.proposal_id} → {saved}")


@proposal_app.command("review")
def proposal_review(
    proposal_id: str = typer.Argument(..., help="Proposal UUID"),
    action: str = typer.Option(..., help="comment|revision|reject|withdraw"),
    reviewer_id: str = typer.Option(..., help="Reviewer identifier"),
    comment: Optional[str] = typer.Option(None, help="Comment or reason"),
):
    """Review a proposal (does not touch ttod.yml)."""
    store = _proposal_store()
    proposal = store.load(proposal_id)

    if action == "comment":
        if not comment:
            typer.echo("--comment required for comment action")
            raise typer.Exit(1)
        proposal.add_comment(reviewer_id, comment)
    elif action == "revision":
        if not comment:
            typer.echo("--comment required for revision action")
            raise typer.Exit(1)
        proposal.request_revision(reviewer_id, comment)
    elif action == "reject":
        proposal.reject(reviewer_id, comment)
    elif action == "withdraw":
        proposal.withdraw(reviewer_id, comment)
    else:
        typer.echo(f"Unknown action: {action}")
        raise typer.Exit(1)

    store.save(proposal)
    typer.echo(f"Proposal {proposal_id} → {proposal.status.value}")


@proposal_app.command("accept")
def proposal_accept(
    proposal_id: str = typer.Argument(..., help="Proposal UUID"),
    reviewer_id: str = typer.Option(..., help="Human reviewer identifier (required)"),
    file: Optional[Path] = typer.Option(None, "--file", help="Target TTOD YAML"),
    allow_unknown_tags: bool = typer.Option(
        False,
        "--allow-unknown-tags",
        help="Allow tags outside taxonomy (default: reject)",
    ),
):
    """Accept a proposal into ttod.yml via atomic write transaction."""
    store = _proposal_store()
    proposal = store.load(proposal_id)
    repo = _repo(file)

    try:
        result = repo.accept_proposal(
            proposal,
            reviewer_id,
            reject_unknown_tags=not allow_unknown_tags,
        )
    except RepositoryError as exc:
        typer.echo(f"ACCEPT FAILED: {exc}")
        raise typer.Exit(1)

    store.save(proposal)
    typer.echo(f"Accepted {result.quote_id} from proposal {result.proposal_id}")


@app.command()
def deprecate(
    quote_id: str = typer.Argument(..., help="Canonical quote ID"),
    deprecated_by: Optional[str] = typer.Option(None, help="Successor quote ID"),
    file: Optional[Path] = typer.Option(None, "--file", help="Target TTOD YAML"),
):
    """Mark a quote deprecated (never deletes)."""
    try:
        _repo(file).deprecate_quote(quote_id, deprecated_by=deprecated_by)
    except RepositoryError as exc:
        typer.echo(f"DEPRECATE FAILED: {exc}")
        raise typer.Exit(1)
    typer.echo(f"Deprecated: {quote_id}")


@app.command()
def erase(
    quote_id: str = typer.Argument(..., help="Canonical quote ID"),
    authority: str = typer.Option(..., help="Erasure authority (required)"),
    decision_ref: str = typer.Option(..., help="Institutional decision reference (required)"),
    reason: Optional[str] = typer.Option(None, help="Erasure reason"),
    file: Optional[Path] = typer.Option(None, "--file", help="Target TTOD YAML"),
):
    """Higher-law erasure tombstone — requires explicit authority and decision reference."""
    try:
        _repo(file).erase_quote(
            quote_id,
            authority=authority,
            decision_ref=decision_ref,
            reason=reason,
        )
    except RepositoryError as exc:
        typer.echo(f"ERASE FAILED: {exc}")
        raise typer.Exit(1)
    typer.echo(f"Erased (tombstone): {quote_id}")


@app.command()
def add(
    section: str = typer.Option(..., help="Section ID"),
    level: str = typer.Option("intermediate", help="Level"),
    text: str = typer.Option(..., help="The wisdom text"),
    lang: str = typer.Option("en", help="ISO 639-1 language (default en)"),
    origin: str = typer.Option("human", help="Origin: human/studio/blackbox"),
    tags: str = typer.Option("", help="Comma-separated tags"),
    reviewer_id: str = typer.Option(..., help="Human reviewer ID (required — no bypass)"),
    file: Optional[Path] = typer.Option(None, "--file", help="Target TTOD YAML"),
    allow_unknown_tags: bool = typer.Option(False, "--allow-unknown-tags"),
):
    """
    Add a quote via proposal+accept transaction (same path as proposal accept).

    Does not bypass review or locking rules.
    """
    if level not in VALID_LEVELS:
        typer.echo(f"Invalid level: {level}")
        raise typer.Exit(1)
    if not re.fullmatch(r"[a-z]{2}", lang):
        typer.echo(f"Invalid lang (expect ISO 639-1): {lang}")
        raise typer.Exit(1)

    candidate: dict[str, Any] = {
        "text": text,
        "section": section,
        "level": level,
        "lang": lang,
        "origin": origin,
    }
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if tag_list:
        candidate["tags"] = tag_list

    try:
        result = _repo(file).accept_quote_direct(
            candidate,
            reviewer_id,
            reject_unknown_tags=not allow_unknown_tags,
        )
    except RepositoryError as exc:
        typer.echo(f"ADD FAILED: {exc}")
        raise typer.Exit(1)

    typer.echo(f"Added: {result.quote_id} ({section}/{level})")


@app.command("translate-draft")
def translate_draft(
    source_id: str = typer.Argument(..., help="Canonical source quote ID to translate"),
    to: str = typer.Option(..., "--to", help="Target ISO 639-1 language (e.g. es)"),
    model: str = typer.Option("qwen3.8:27b", "--model", help="Ollama model tag to run"),
    host: str = typer.Option(OLLAMA_DEFAULT_HOST, "--host", help="Ollama API host"),
    timeout: float = typer.Option(180.0, "--timeout", help="Ollama call timeout (seconds)"),
    proposer_id: str = typer.Option("cli-translate-draft", help="Proposer identifier recorded on the proposal"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML source (default: live ttod.yml, read-only)"),
    output: Optional[Path] = typer.Option(None, "--output", help="Write proposal JSON here in addition to the store"),
):
    """
    Draft a sister-language translation of SOURCE_ID via local Ollama and save it as a
    `status: proposed` proposal. Never touches ttod.yml and never sets `status: active` —
    a human runs `proposal review` then `proposal accept --reviewer-id ...` separately.

    Explicit command only — not a side effect of `add` or `proposal accept` (Phase S §S4').
    """
    if not re.fullmatch(r"[a-z]{2}", to):
        typer.echo(f"Invalid --to (expect ISO 639-1, e.g. es): {to}")
        raise typer.Exit(1)

    root = _repo(file).load()
    quotes = root.get("quotes", [])
    source = next((q for q in quotes if isinstance(q, dict) and q.get("id") == source_id), None)
    if source is None:
        typer.echo(f"Source quote not found: {source_id}")
        raise typer.Exit(1)

    source_lang = source.get("lang")
    if not source_lang:
        typer.echo(f"Source quote '{source_id}' has no 'lang' field — cannot translate")
        raise typer.Exit(1)

    # Fail fast #1 (S4' 2026-09-06 addition): same-language target would trip
    # TRANSLATION_SAME_LANGUAGE at accept time regardless — refuse before calling any model.
    if to == source_lang:
        typer.echo(
            f"REFUSED: --to '{to}' equals source quote '{source_id}'s own lang '{source_lang}' "
            f"(would trip TRANSLATION_SAME_LANGUAGE at accept time — no model call made)"
        )
        raise typer.Exit(2)

    # Fail fast #2 (S4' 2026-09-06 addition): warn, do not hard-block — a human may
    # deliberately want a second candidate to compare before accepting either.
    existing = find_active_translations(quotes, source_id, to)
    if existing:
        typer.echo(
            f"WARNING: an active translation of '{source_id}' into '{to}' already exists: "
            f"{existing} — accepting a second active one would trip TRANSLATION_DUPLICATE_ACTIVE. "
            f"Proceeding anyway (a human may want a second candidate to compare)."
        )

    try:
        draft = translate_quote(
            model,
            source_lang,
            to,
            source.get("text", ""),
            source.get("teaches"),
            host=host,
            timeout=timeout,
        )
    except TranslationError as exc:
        typer.echo(f"TRANSLATE-DRAFT FAILED: {exc}")
        raise typer.Exit(1)

    candidate = build_translation_candidate(source, source_id, to, draft)

    proposal = create_proposal(
        candidate_content=candidate,
        proposer_kind="model",
        proposer_id=proposer_id,
        generation_method=f"ollama:{draft.model}:translate-draft-v1",
    )

    saved_path = _proposal_store().save(proposal)
    if output:
        output.write_text(json.dumps(proposal.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    typer.echo(f"Drafted translation proposal: {proposal.proposal_id}")
    typer.echo(f"  model: {draft.model} ({draft.latency_s:.1f}s)")
    typer.echo(f"  source: {source_id} ({source_lang}) -> target lang: {to}")
    typer.echo(f"  text: {draft.text}")
    if draft.teaches is not None:
        typer.echo(f"  teaches: {draft.teaches}")
    typer.echo(f"  saved: {saved_path}")
    typer.echo(
        "Status: proposed (never active). Next: `proposal review` then "
        f"`proposal accept {proposal.proposal_id} --reviewer-id <you>` — a separate, deliberate human action."
    )


@app.command("translate-batch")
def translate_batch(
    to: str = typer.Option("es", "--to", help="Target ISO 639-1 language"),
    model: str = typer.Option("qwen3.8:27b", "--model", help="Ollama model tag to run"),
    host: str = typer.Option(OLLAMA_DEFAULT_HOST, "--host", help="Ollama API host"),
    timeout: float = typer.Option(180.0, "--timeout", help="Per-record Ollama timeout in seconds"),
    proposer_id: str = typer.Option("cli-translate-batch", help="Proposer identifier recorded on proposals"),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        min=1,
        help="Maximum records to draft in this tranche. Required unless --all is set.",
    ),
    all_records: bool = typer.Option(
        False,
        "--all",
        help="Draft every currently eligible record. Use only after S5 editorial gates are frozen.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="List selected source IDs without calling Ollama"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML source (default: live ttod.yml, read-only)"),
    manifest_dir: Path = typer.Option(
        DEFAULT_PROPOSALS / "manifests",
        "--manifest-dir",
        help="Directory for batch manifests",
    ),
):
    """
    Draft a resumable tranche of translation proposals.

    This command never accepts proposals and never writes ttod.yml. It recomputes
    eligible English originals, skips completed active translations, skips
    already-pending translation proposals for the same source/target, and writes
    a manifest for editorial review.
    """
    if not re.fullmatch(r"[a-z]{2}", to):
        typer.echo(f"Invalid --to (expect ISO 639-1, e.g. es): {to}")
        raise typer.Exit(1)
    if not all_records and limit is None:
        typer.echo("REFUSED: set --limit for a bounded tranche, or pass --all explicitly.")
        raise typer.Exit(2)

    repo = _repo(file)
    source_bytes = repo.read_bytes()
    root = yaml.safe_load(source_bytes.decode("utf-8"))
    eligible = _eligible_translation_sources(root, to)
    selected = eligible if all_records else eligible[: limit or 0]

    typer.echo(
        f"Eligible sources without active/pending '{to}' translation: {len(eligible)}"
    )
    typer.echo(f"Selected for this tranche: {len(selected)}")
    for quote in selected:
        typer.echo(f"  - {quote['id']} ({quote.get('section')}/{quote.get('level')})")

    if dry_run:
        typer.echo("Dry run only — no model calls, no proposals written.")
        return
    if not selected:
        typer.echo("Nothing to draft.")
        return

    run_id = datetime.now(timezone.utc).strftime("s5-%Y%m%dT%H%M%SZ")
    manifest_dir.mkdir(parents=True, exist_ok=True)
    store = _proposal_store()
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ttod_file": str(repo.path),
        "ttod_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "model": model,
        "host": host,
        "target_lang": to,
        "eligible_count_at_start": len(eligible),
        "selected_source_ids": [q["id"] for q in selected],
        "created_proposals": [],
        "failures": [],
        "canonical_boundary": "proposals only; no proposal accepted; ttod.yml read-only",
    }

    for quote in selected:
        source_id = str(quote["id"])
        source_lang = quote.get("lang")
        try:
            if to == source_lang:
                raise TranslationError(f"target lang equals source lang for {source_id}")
            draft = translate_quote(
                model,
                str(source_lang),
                to,
                quote.get("text", ""),
                quote.get("teaches"),
                host=host,
                timeout=timeout,
            )
            candidate = build_translation_candidate(quote, source_id, to, draft)
            proposal = create_proposal(
                candidate_content=candidate,
                proposer_kind="model",
                proposer_id=proposer_id,
                generation_method=f"ollama:{draft.model}:translate-batch-v1",
            )
            saved_path = store.save(proposal)
            manifest["created_proposals"].append(
                {
                    "source_id": source_id,
                    "proposal_id": proposal.proposal_id,
                    "path": str(saved_path),
                    "latency_s": round(draft.latency_s, 3),
                }
            )
            typer.echo(f"Drafted {source_id} -> {proposal.proposal_id}")
        except Exception as exc:
            manifest["failures"].append({"source_id": source_id, "error": str(exc)})
            typer.echo(f"FAILED {source_id}: {exc}")

    manifest_path = manifest_dir / f"{run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if repo.read_bytes() != source_bytes:
        typer.echo("REFUSED: ttod.yml changed during batch run; proposals remain staged, but source snapshot moved.")
        raise typer.Exit(3)

    typer.echo(f"Manifest: {manifest_path}")
    typer.echo(
        f"Created proposals: {len(manifest['created_proposals'])}; failures: {len(manifest['failures'])}"
    )


@migrate_app.command("prepare")
def migrate_prepare(
    output: Path = typer.Option(
        Path("/tmp/ttod-v3-candidate.yml"),
        "--output",
        help="Write v3 candidate YAML here",
    ),
    file: Optional[Path] = typer.Option(None, "--file", help="Source TTOD YAML (default: ttod.yml)"),
    as_json: bool = typer.Option(False, "--json", help="Emit semantic summary as JSON"),
):
    """Generate a v3 migration candidate in a temporary path (does not modify live file)."""
    repo = _repo(file)
    original_text = repo.path.read_text(encoding="utf-8")
    root = repo.load()
    migrated, summary = migrate_root(root)
    candidate_text = serialize_migrated_document(migrated, original_text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(candidate_text, encoding="utf-8")

    pre = TTODValidator(strict=True).validate_root(migrated)
    if as_json:
        payload = summary.to_dict()
        payload["candidate_path"] = str(output)
        payload["strict_valid"] = pre.is_valid
        payload["error_count"] = len(pre.errors)
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(f"Candidate: {output}")
        typer.echo(json.dumps(summary.to_dict(), indent=2))
        typer.echo(f"Strict validation: {'OK' if pre.is_valid else 'FAIL'} ({len(pre.errors)} errors)")

    if not pre.is_valid:
        raise typer.Exit(1)


@migrate_app.command("apply")
def migrate_apply(
    approve: bool = typer.Option(
        False,
        "--approve",
        help="Required — records operator authorization to replace live ttod.yml",
    ),
    file: Optional[Path] = typer.Option(None, "--file", help="Target TTOD YAML (default: live ttod.yml)"),
):
    """Apply v3 migration to ttod.yml via Q3 atomic write transaction."""
    if not approve:
        typer.echo("REFUSED: --approve required (human authorization for live migration)")
        raise typer.Exit(2)

    repo = _repo(file)
    try:
        summary = repo.apply_v3_migration()
    except RepositoryError as exc:
        typer.echo(f"MIGRATE FAILED: {exc}")
        raise typer.Exit(1)

    typer.echo(json.dumps(summary.to_dict(), indent=2))
    typer.echo("OK — live ttod.yml migrated to v3")


@app.command("bridge-self-test")
def bridge_self_test(
    fixture: Path = typer.Option(
        Path(__file__).parent / "tests/fixtures/q4_roundtrip.json",
        "--fixture",
        help="Round-trip fixture path",
    ),
    file: Path = typer.Option(..., "--file", help="Disposable TTOD YAML copy (required)"),
):
    """Run quote-out → proposal-in → accept round-trip on a fixture (never live ttod.yml)."""
    from ttod_core.bridge_self_test import run_bridge_self_test

    if file.resolve() == DEFAULT_TTOD.resolve():
        typer.echo("REFUSED: --file must be a disposable copy, not live ttod.yml")
        raise typer.Exit(2)

    try:
        result = run_bridge_self_test(fixture, file)
    except Exception as exc:
        typer.echo(f"BRIDGE SELF-TEST FAILED: {exc}")
        raise typer.Exit(1)

    typer.echo(json.dumps(result, indent=2))
    if not result.get("wpl_record_digest_preserved"):
        raise typer.Exit(1)
    typer.echo("OK — bridge round-trip passed")


@bridge_app.command("quote-out")
def bridge_quote_out(
    quote_id: str = typer.Argument(..., help="Canonical quote ID"),
    snapshot: Path = typer.Option(..., "--snapshot", help="Q2E JSON snapshot path (not ttod.yml)"),
    output: Optional[Path] = typer.Option(None, "--output", help="Write transport JSON here"),
):
    """Export a quote-out transport payload from a Q2E snapshot."""
    if snapshot.suffix in (".yml", ".yaml"):
        typer.echo("REFUSED: read Q2E export JSON, never ttod.yml")
        raise typer.Exit(2)

    data = json.loads(snapshot.read_text(encoding="utf-8"))
    manifest = data.get("_manifest", {})
    snapshot_digest = manifest.get("snapshot_digest")
    if not snapshot_digest:
        typer.echo("Snapshot missing _manifest.snapshot_digest")
        raise typer.Exit(1)

    quotes = data.get("quotes", [])
    quote = next((q for q in quotes if q.get("id") == quote_id), None)
    if quote is None:
        typer.echo(f"Quote not found in snapshot: {quote_id}")
        raise typer.Exit(1)

    bridge = TTODBridge()
    try:
        transport = bridge.export_quote_out(quote, snapshot_digest)
    except BridgeError as exc:
        typer.echo(f"QUOTE-OUT FAILED: {exc}")
        raise typer.Exit(1)

    payload = json.dumps(transport, indent=2, ensure_ascii=False)
    if output:
        output.write_text(payload + "\n", encoding="utf-8")
        typer.echo(f"Quote-out written: {output}")
    else:
        typer.echo(payload)


@bridge_app.command("proposal-in")
def bridge_proposal_in(
    path: Path = typer.Argument(..., help="Proposal-in transport JSON"),
    store: bool = typer.Option(True, help="Save to proposals store"),
):
    """Import proposal-in transport into proposals store (does not accept or write ttod.yml)."""
    transport = json.loads(path.read_text(encoding="utf-8"))
    bridge = TTODBridge()
    try:
        proposal = bridge.import_proposal_in(transport)
    except BridgeError as exc:
        typer.echo(f"PROPOSAL-IN FAILED: {exc}")
        raise typer.Exit(1)

    if store:
        saved = _proposal_store().save(proposal)
        typer.echo(f"Imported proposal {proposal.proposal_id} → {saved}")
    else:
        typer.echo(json.dumps(proposal.to_dict(), indent=2))


@app.command()
def graph(
    output: Optional[Path] = typer.Option(None, "--output", help="Output path"),
    file: Optional[Path] = typer.Option(None, "--file", help="TTOD YAML source"),
):
    """Export graph projection (alias for export --format graph)."""
    export(format="graph", output=output, file=file)


if __name__ == "__main__":
    app()
