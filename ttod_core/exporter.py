"""
TTOD Exporter (Q2E)

Atomic export mechanics for JSON and graph exports.

Implements the atomic write sequence:
1. Write to sibling temporary file in same directory as target
2. Flush and fsync the temp file
3. Validate the written bytes (re-read and compare to intended C14N bytes)
4. Atomically rename the temp file over the target
5. Never create the target *file* before validation succeeds
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from ttod_core.canonical import (
    CanonicalizationError,
    Canonicalizer,
    ExportPolicy,
    SnapshotManifest,
)


class ExportError(Exception):
    """Raised when export fails."""


class Exporter:
    """Atomic TTOD exporter."""

    def __init__(self, canonicalizer: Optional[Canonicalizer] = None):
        """Initialize exporter with optional canonicalizer."""
        self.canonicalizer = canonicalizer or Canonicalizer()

    def export_json(
        self,
        data: Dict[str, Any],
        target_path: Path,
        export_policy: Optional[ExportPolicy] = None,
        generated_at: Optional[str] = None,
    ) -> SnapshotManifest:
        """
        Export data to canonical JSON atomically.

        `generated_at` is returned on the Python manifest object but is omitted
        from the written file so two exports of the same state are byte-identical.
        """
        export_data, manifest = self._build_json_export(data, export_policy, generated_at)
        self._write_atomically(export_data, target_path)
        return manifest

    def export_graph(
        self,
        data: Dict[str, Any],
        target_path: Path,
        export_policy: Optional[ExportPolicy] = None,
        generated_at: Optional[str] = None,
    ) -> SnapshotManifest:
        """
        Export a deterministic read-only graph projection (nodes + typed edges).

        This is the lossless structural interchange Q2E owes; a writable graph
        backend is out of scope (studio RFC, post-Q).
        """
        if export_policy is None:
            export_policy = ExportPolicy()

        json_export, manifest = self._build_json_export(data, export_policy, generated_at)
        quotes = json_export.get("quotes", [])
        graph = {
            "algorithm": "TTOD-C14N-v1",
            "projection": "graph-v1",
            "_manifest": json_export["_manifest"],
            "nodes": self._graph_nodes(quotes),
            "edges": self._graph_edges(quotes),
        }
        self._write_atomically(graph, target_path)
        return manifest

    def export_quote_json(
        self,
        quote: Dict[str, Any],
        target_path: Path,
    ) -> str:
        """Export a single quote to canonical JSON atomically."""
        content_digest = self.canonicalizer.verify_content_digest(quote)
        export_quote = {**quote, "content_digest": content_digest}
        self._write_atomically(export_quote, target_path)
        return content_digest

    def _build_json_export(
        self,
        data: Dict[str, Any],
        export_policy: Optional[ExportPolicy],
        generated_at: Optional[str],
    ) -> tuple:
        if export_policy is None:
            export_policy = ExportPolicy()

        quotes = data.get("quotes", [])
        filtered_quotes = [q for q in quotes if export_policy.should_include(q)]

        export_data = {k: v for k, v in data.items() if k != "quotes"}
        export_data["quotes"] = filtered_quotes

        source_digest = self.canonicalizer.compute_source_digest(
            self.canonicalizer.to_canonical_json(data)
        )
        taxonomy_digest = self.canonicalizer.compute_taxonomy_digest(data.get("tag_taxonomy", {}))
        collection_policy_digest = self.canonicalizer.compute_collection_policy_digest(
            data.get("collections", {})
        )
        snapshot_digest = self.canonicalizer.compute_snapshot_digest(
            filtered_quotes,
            data.get("meta", {}).get("version", "3.1.0"),
            taxonomy_digest,
            collection_policy_digest,
        )

        manifest = self.canonicalizer.create_manifest(
            source_digest=source_digest,
            record_count=len(filtered_quotes),
            export_policy=export_policy,
            snapshot_digest=snapshot_digest,
            schema_version=data.get("meta", {}).get("version", "3.1.0"),
            generated_at=generated_at if generated_at is not None else "",
        )

        written_manifest = manifest.to_dict()
        written_manifest.pop("generated_at", None)
        export_data["_manifest"] = written_manifest
        return export_data, manifest

    def _graph_nodes(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        nodes = []
        for quote in quotes:
            nodes.append(
                {
                    "id": quote.get("id"),
                    "section": quote.get("section"),
                    "origin": quote.get("origin"),
                    "status": quote.get("status", "active"),
                    "text": quote.get("text"),
                    "lang": quote.get("lang"),
                }
            )
        return sorted(nodes, key=lambda n: n.get("id") or "")

    def _graph_edges(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        edges: List[Dict[str, Any]] = []
        for quote in quotes:
            source = quote.get("id")
            for target in quote.get("related") or []:
                edges.append({"source": source, "target": target, "rel": "related"})
            for edge in quote.get("relation_edges") or []:
                if isinstance(edge, dict):
                    edges.append(
                        {
                            "source": source,
                            "target": edge.get("target"),
                            "rel": edge.get("relation_type") or "related",
                        }
                    )
            for target in quote.get("immediate_parent_refs") or []:
                edges.append({"source": source, "target": target, "rel": "immediate_parent"})
            for target in quote.get("root_source_refs") or []:
                edges.append({"source": source, "target": target, "rel": "root_source"})
            deprecated_by = quote.get("deprecated_by")
            if deprecated_by:
                edges.append({"source": source, "target": deprecated_by, "rel": "deprecated_by"})
            superseded_by = quote.get("superseded_by")
            if superseded_by:
                edges.append({"source": source, "target": superseded_by, "rel": "superseded_by"})
        return sorted(edges, key=lambda e: (e.get("source") or "", e.get("rel") or "", e.get("target") or ""))

    def _write_atomically(self, data: Any, target_path: Path) -> None:
        """Write C14N bytes to target path atomically."""
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            json_bytes = self.canonicalizer.to_canonical_json(data)
        except CanonicalizationError as exc:
            raise ExportError(f"Canonicalization failed: {exc}") from exc

        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=target_path.parent,
            prefix=f".{target_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            try:
                temp_file.write(json_bytes)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_file.close()

                written_bytes = temp_path.read_bytes()
                if written_bytes != json_bytes:
                    raise ExportError("Re-read bytes do not match intended C14N payload")

                temp_path.replace(target_path)
            except Exception as exc:
                if temp_path.exists():
                    temp_path.unlink()
                if isinstance(exc, ExportError):
                    raise
                raise ExportError(f"Atomic write failed: {exc}") from exc
