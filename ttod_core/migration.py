"""
TTOD v2.2 → v3.0 migration (Phase Q6).

Generates a v3 candidate without inventing authorship facts. Gaps become explicit
legacy-unknown / unresolved states. Numeric tag scalars are coerced to strings
only through logged migration decisions (Q6 §2.3).
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml

from ttod_core.canonical import Canonicalizer
from ttod_core.repository import compute_derived_metadata

SCHEMA_VERSION = "3.0.0"
DEFAULT_HOLDER = "ruvebal@crea-comm.net"
DEFAULT_LICENSE = "CC-BY-NC-SA-4.0"
DEFAULT_PERMISSION_BASIS = "rights-holder-relicense-2026-08-18"
MIGRATION_CLOSURE_CATEGORY = "migration_closure"


@dataclass
class MigrationDecision:
    """Logged migration transformation."""

    rule: str
    quote_id: str
    detail: str


@dataclass
class SemanticDiffSummary:
    """Human-readable migration summary (not a raw YAML diff)."""

    quotes_total: int
    origin_legacy_unknown: int = 0
    numeric_tags_coerced: int = 0
    tags_added_to_taxonomy: int = 0
    schema_version_added: int = 0
    content_digests_computed: int = 0
    rights_defaults_applied: int = 0
    blackbox_downgraded_to_legacy: int = 0
    meta_version: str = ""
    decisions: List[MigrationDecision] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quotes_total": self.quotes_total,
            "origin_legacy_unknown": self.origin_legacy_unknown,
            "numeric_tags_coerced": self.numeric_tags_coerced,
            "tags_added_to_taxonomy": self.tags_added_to_taxonomy,
            "schema_version_added": self.schema_version_added,
            "content_digests_computed": self.content_digests_computed,
            "rights_defaults_applied": self.rights_defaults_applied,
            "blackbox_downgraded_to_legacy": self.blackbox_downgraded_to_legacy,
            "meta_version": self.meta_version,
            "decision_count": len(self.decisions),
        }


def migrate_root(root: Dict[str, Any]) -> Tuple[Dict[str, Any], SemanticDiffSummary]:
    """Return a migrated copy of root and a semantic diff summary."""
    migrated = copy.deepcopy(root)
    summary = SemanticDiffSummary(quotes_total=len(migrated.get("quotes", [])))
    canonicalizer = Canonicalizer()

    meta = migrated.setdefault("meta", {})
    meta["version"] = SCHEMA_VERSION
    summary.meta_version = SCHEMA_VERSION

    _coerce_quote_tags(migrated.get("quotes", []), summary)
    _normalize_dates_tree(migrated, summary)
    _normalize_origins(migrated.get("quotes", []), summary)
    _apply_schema_version(migrated.get("quotes", []), summary)
    _apply_default_rights(migrated.get("quotes", []), summary)
    _close_tag_taxonomy(migrated, summary)
    _compute_digests(migrated.get("quotes", []), canonicalizer, summary)
    _recompute_meta(migrated)

    return migrated, summary


def _coerce_quote_tags(quotes: List[Dict[str, Any]], summary: SemanticDiffSummary) -> None:
    for quote in quotes:
        tags = quote.get("tags")
        if not isinstance(tags, list):
            continue
        new_tags: List[str] = []
        for tag in tags:
            if isinstance(tag, (int, float)):
                coerced = str(int(tag)) if isinstance(tag, float) and tag.is_integer() else str(tag)
                summary.numeric_tags_coerced += 1
                summary.decisions.append(
                    MigrationDecision(
                        "numeric_tag_coercion",
                        quote.get("id", "<unknown>"),
                        f"{tag!r} → {coerced!r}",
                    )
                )
                new_tags.append(coerced)
            elif tag is not None:
                new_tags.append(str(tag))
        quote["tags"] = new_tags


def _normalize_dates_tree(node: Any, summary: SemanticDiffSummary, *, path: str = "") -> None:
    """Coerce YAML date/datetime scalars anywhere in the document tree to ISO strings."""
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}" if path else key
            if isinstance(value, datetime):
                node[key] = value.date().isoformat()
                summary.decisions.append(
                    MigrationDecision("date_coercion", child_path, "datetime → ISO date string")
                )
            elif isinstance(value, date):
                node[key] = value.isoformat()
                summary.decisions.append(
                    MigrationDecision("date_coercion", child_path, "date → ISO date string")
                )
            else:
                _normalize_dates_tree(value, summary, path=child_path)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _normalize_dates_tree(item, summary, path=f"{path}[{index}]")


def _normalize_origins(quotes: List[Dict[str, Any]], summary: SemanticDiffSummary) -> None:
    for quote in quotes:
        origin = quote.get("origin")
        if origin is None:
            quote["origin"] = "legacy-unknown"
            summary.origin_legacy_unknown += 1
            summary.decisions.append(
                MigrationDecision("origin_legacy_unknown", quote.get("id", "<unknown>"), "missing origin")
            )
            continue

        if origin == "blackbox":
            validation = quote.get("validation") or {}
            if validation.get("status") != "validated" or not validation.get("reviewer_id"):
                quote["origin"] = "legacy-unknown"
                summary.blackbox_downgraded_to_legacy += 1
                summary.decisions.append(
                    MigrationDecision(
                        "blackbox_without_review",
                        quote.get("id", "<unknown>"),
                        "blackbox without validated human review → legacy-unknown",
                    )
                )


def _apply_schema_version(quotes: List[Dict[str, Any]], summary: SemanticDiffSummary) -> None:
    for quote in quotes:
        if quote.get("schema_version") != SCHEMA_VERSION:
            quote["schema_version"] = SCHEMA_VERSION
            summary.schema_version_added += 1


def _apply_default_rights(quotes: List[Dict[str, Any]], summary: SemanticDiffSummary) -> None:
    """Apply Q0 frozen default rights for rights-holder records without item rights."""
    for quote in quotes:
        if quote.get("rights"):
            continue
        quote["rights"] = {
            "access": "public",
            "license": DEFAULT_LICENSE,
            "holder": DEFAULT_HOLDER,
            "permission_basis": DEFAULT_PERMISSION_BASIS,
        }
        summary.rights_defaults_applied += 1
        summary.decisions.append(
            MigrationDecision(
                "rights_default_q0",
                quote.get("id", "<unknown>"),
                f"applied {DEFAULT_LICENSE} per Q0 decision",
            )
        )


def _flatten_taxonomy(tag_taxonomy: Dict[str, Any]) -> Set[str]:
    declared: Set[str] = set()
    for tags in tag_taxonomy.values():
        if isinstance(tags, list):
            declared.update(str(t) for t in tags)
        elif isinstance(tags, dict):
            declared.update(str(k) for k in tags.keys())
    return declared


def _close_tag_taxonomy(root: Dict[str, Any], summary: SemanticDiffSummary) -> None:
    """Mechanically close tag_taxonomy from quote usage (migration_closure bucket)."""
    tag_taxonomy = root.setdefault("tag_taxonomy", {})
    declared = _flatten_taxonomy(tag_taxonomy)
    used: Set[str] = set()
    for quote in root.get("quotes", []):
        for tag in quote.get("tags") or []:
            used.add(str(tag))

    missing = sorted(used - declared)
    if not missing:
        return

    closure = list(tag_taxonomy.get(MIGRATION_CLOSURE_CATEGORY, []))
    if not isinstance(closure, list):
        closure = []
    existing_closure = set(str(t) for t in closure)

    for tag in missing:
        if tag not in existing_closure:
            closure.append(tag)
            summary.tags_added_to_taxonomy += 1
            summary.decisions.append(
                MigrationDecision("tag_taxonomy_closure", "<taxonomy>", f"added {tag!r} to migration_closure")
            )

    tag_taxonomy[MIGRATION_CLOSURE_CATEGORY] = sorted(closure)


def _compute_digests(
    quotes: List[Dict[str, Any]],
    canonicalizer: Canonicalizer,
    summary: SemanticDiffSummary,
) -> None:
    for quote in quotes:
        quote["content_digest"] = canonicalizer.compute_content_digest(quote)
        summary.content_digests_computed += 1


def _recompute_meta(root: Dict[str, Any]) -> None:
    derived = compute_derived_metadata(root)
    meta = root.setdefault("meta", {})
    meta["total_quotes"] = derived.total_quotes
    meta["last_id_by_section"] = dict(sorted(derived.last_id_by_section.items()))


def write_candidate(root: Dict[str, Any], path: Path) -> None:
    """Write migrated candidate YAML to a temporary path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(root, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_header_comment_block(text: str) -> str:
    """Return the leading comment banner before the first root YAML key."""
    import re

    lines = text.splitlines()
    header: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            header.append(line)
            continue
        if stripped.startswith("#"):
            header.append(line)
            continue
        if re.match(r"^[a-z][a-z0-9_]*:", stripped):
            break
        header.append(line)
    return "\n".join(header) + "\n" if header else ""


def serialize_migrated_document(root: Dict[str, Any], original_text: str) -> str:
    """Serialize migrated root with updated header comments preserved."""
    header = update_header_comment_block(extract_header_comment_block(original_text))
    body = yaml.dump(root, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return header + body


def update_header_comment_block(original_text: str) -> str:
    """Update ttod.yml header license and schema version lines."""
    lines = original_text.splitlines()
    out: List[str] = []
    for line in lines:
        if line.startswith("# Schema Version:"):
            out.append("# Schema Version: 3.0.0")
        elif line.startswith("# License:"):
            out.append("# License: CC BY-NC-SA 4.0 (content) — see LICENSE-CONTENT; code MIT — see LICENSE-CODE")
        elif line.startswith("# Updated:"):
            out.append(f"# Updated: {date.today().isoformat()}")
        else:
            out.append(line)
    return "\n".join(out) + "\n"
