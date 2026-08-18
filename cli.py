#!/usr/bin/env python3
"""
TTOD CLI — The Tao of Development
Validate, query, export, and grow the pedagogical wisdom database.

Usage:
    python cli.py validate
    python cli.py stats
    python cli.py export --format json
    python cli.py add --section architecture --level advanced --text "..."
    python cli.py graph
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(help="The Tao of Development — pedagogical wisdom CLI")

TTOD_PATH = Path(__file__).parent / "ttod.yml"
EXPORTS_DIR = Path(__file__).parent / "exports"

VALID_LEVELS = {"beginner", "intermediate", "advanced", "master"}
VALID_ORIGINS = {"human", "studio", "blackbox"}


def load_ttod() -> dict[str, Any]:
    """Load and return the full TTOD database."""
    return yaml.safe_load(TTOD_PATH.read_text(encoding="utf-8"))


def get_quotes(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract quotes list from TTOD data."""
    return data.get("quotes", [])


def get_sections(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract section definitions."""
    return data.get("sections", [])


@app.command()
def validate():
    """Validate ttod.yml against schema rules."""
    data = load_ttod()
    quotes = get_quotes(data)
    sections = get_sections(data)

    section_ids = {s["id"] for s in sections}
    section_prefixes = {s["prefix"]: s["id"] for s in sections}
    all_ids = {q["id"] for q in quotes}
    errors: list[str] = []

    for i, q in enumerate(quotes):
        qid = q.get("id", f"<missing-id at index {i}>")

        # Required fields
        for field in ("id", "text", "section", "level"):
            if field not in q:
                errors.append(f"{qid}: missing required field '{field}'")

        # Level validation
        level = q.get("level")
        if level and level not in VALID_LEVELS:
            errors.append(f"{qid}: invalid level '{level}'")

        # Section validation
        section = q.get("section")
        if section and section not in section_ids:
            errors.append(f"{qid}: unknown section '{section}'")

        # ID prefix matches section
        if "id" in q and "section" in q:
            prefix = q["id"].rsplit("-", 1)[0]
            expected_section = section_prefixes.get(prefix)
            if expected_section and expected_section != q["section"]:
                errors.append(f"{qid}: prefix '{prefix}' maps to '{expected_section}', not '{q['section']}'")

        # Related IDs exist
        for rel_id in q.get("related", []):
            if rel_id not in all_ids:
                errors.append(f"{qid}: related ID '{rel_id}' not found")

        # Origin validation (optional field)
        origin = q.get("origin")
        if origin and origin not in VALID_ORIGINS:
            errors.append(f"{qid}: invalid origin '{origin}'")

    # Duplicate ID check
    id_counts = Counter(q.get("id") for q in quotes)
    for qid, count in id_counts.items():
        if count > 1:
            errors.append(f"{qid}: duplicate ID ({count} occurrences)")

    if errors:
        typer.echo(f"FAIL — {len(errors)} errors:")
        for e in errors:
            typer.echo(f"  - {e}")
        raise typer.Exit(1)
    else:
        typer.echo(f"OK — {len(quotes)} quotes validated, 0 errors.")


@app.command()
def stats():
    """Show statistics breakdown."""
    data = load_ttod()
    quotes = get_quotes(data)

    typer.echo(f"Total quotes: {len(quotes)}\n")

    typer.echo("By section:")
    for section, count in sorted(Counter(q.get("section") for q in quotes).items(), key=lambda x: -x[1]):
        typer.echo(f"  {section}: {count}")

    typer.echo("\nBy level:")
    for level, count in sorted(Counter(q.get("level") for q in quotes).items(), key=lambda x: -x[1]):
        typer.echo(f"  {level}: {count}")

    typer.echo("\nBy origin:")
    origin_counts = Counter(q.get("origin", "human") for q in quotes)
    for origin, count in sorted(origin_counts.items(), key=lambda x: -x[1]):
        typer.echo(f"  {origin}: {count}")

    # Tag frequency
    all_tags: list[str] = []
    for q in quotes:
        all_tags.extend(q.get("tags", []))
    typer.echo(f"\nUnique tags: {len(set(all_tags))}")
    typer.echo("Top 10 tags:")
    for tag, count in Counter(all_tags).most_common(10):
        typer.echo(f"  {tag}: {count}")


@app.command()
def export(
    format: str = typer.Option("json", help="Export format: json, graph"),
    output: Path = typer.Option(None, help="Output file path"),
):
    """Export TTOD to JSON or graph format."""
    data = load_ttod()
    EXPORTS_DIR.mkdir(exist_ok=True)

    if format == "json":
        out_path = output or EXPORTS_DIR / "ttod.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        typer.echo(f"Exported to {out_path}")

    elif format == "graph":
        out_path = output or EXPORTS_DIR / "graph.json"
        quotes = get_quotes(data)
        nodes = []
        edges = []
        for q in quotes:
            nodes.append({
                "id": q["id"],
                "label": q["text"][:80],
                "section": q.get("section"),
                "level": q.get("level"),
                "tags": q.get("tags", []),
            })
            for rel_id in q.get("related", []):
                edges.append({"source": q["id"], "target": rel_id, "type": "semantic_link"})

        graph = {"nodes": nodes, "edges": edges}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        typer.echo(f"Graph exported: {len(nodes)} nodes, {len(edges)} edges → {out_path}")

    else:
        typer.echo(f"Unknown format: {format}")
        raise typer.Exit(1)


@app.command()
def add(
    section: str = typer.Option(..., help="Section ID"),
    level: str = typer.Option("intermediate", help="Level: beginner/intermediate/advanced/master"),
    text: str = typer.Option(..., help="The wisdom text"),
    subsection: str = typer.Option(None, help="Subsection"),
    teaches: str = typer.Option(None, help="What it teaches"),
    origin: str = typer.Option("studio", help="Origin: human/studio/blackbox"),
    tags: str = typer.Option("", help="Comma-separated tags"),
):
    """Add a new quote to ttod.yml."""
    data = load_ttod()
    sections = get_sections(data)
    section_map = {s["id"]: s for s in sections}

    if section not in section_map:
        typer.echo(f"Unknown section: {section}. Available: {list(section_map.keys())}")
        raise typer.Exit(1)

    if level not in VALID_LEVELS:
        typer.echo(f"Invalid level: {level}. Use: {VALID_LEVELS}")
        raise typer.Exit(1)

    # Generate next ID
    prefix = section_map[section]["prefix"]
    existing_ids = [q["id"] for q in get_quotes(data) if q["id"].startswith(prefix + "-")]
    max_num = max((int(qid.split("-")[1]) for qid in existing_ids), default=0)
    new_id = f"{prefix}-{max_num + 1:03d}"

    new_quote: dict[str, Any] = {
        "id": new_id,
        "text": text,
        "section": section,
        "level": level,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "origin": origin,
        "created_at": str(date.today()),
    }
    if subsection:
        new_quote["subsection"] = subsection
    if teaches:
        new_quote["teaches"] = teaches

    # Append to YAML (load raw, append, write)
    raw = TTOD_PATH.read_text(encoding="utf-8")
    quote_yaml = yaml.dump([new_quote], default_flow_style=False, allow_unicode=True)
    # Indent to match existing structure (1 space for list items)
    indented = "\n" + "\n".join(" " + line for line in quote_yaml.strip().split("\n"))
    raw = raw.rstrip() + "\n" + indented + "\n"
    TTOD_PATH.write_text(raw, encoding="utf-8")

    typer.echo(f"Added: {new_id} ({section}/{level})")
    typer.echo(f"  \"{text[:80]}...\"" if len(text) > 80 else f"  \"{text}\"")


@app.command()
def graph():
    """Export graph data for 3D visualization."""
    export(format="graph")


if __name__ == "__main__":
    app()
