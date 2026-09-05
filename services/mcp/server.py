"""Read-only FastMCP retrieval service for the TTOD corpus."""

from __future__ import annotations

import hashlib
import json
import math
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from ttod_core.exporter import Exporter
from ttod_core.sensors.rights import check_rights_public_export

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "ttod.yml"


class EmbeddingError(RuntimeError):
    """Raised when Ollama cannot return a valid embedding."""


def _ollama_embed(text: str) -> list[float]:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_EMBED_MODEL")
    if not model:
        raise EmbeddingError("OLLAMA_EMBED_MODEL must be set")
    body = json.dumps({"model": model, "input": text}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/embed",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise EmbeddingError(f"Ollama embedding request failed: {exc}") from exc
    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list) or not embeddings or not isinstance(embeddings[0], list):
        raise EmbeddingError("Ollama returned no embedding vector")
    return [float(value) for value in embeddings[0]]


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("embedding dimensions must match and be non-empty")
    denominator = math.sqrt(sum(v * v for v in left)) * math.sqrt(sum(v * v for v in right))
    return sum(a * b for a, b in zip(left, right)) / denominator if denominator else 0.0


def _is_public_active(quote: dict[str, Any]) -> bool:
    rights = quote.get("rights")
    return (
        quote.get("status", "active") == "active"
        and isinstance(rights, dict)
        and rights.get("access") == "public"
        and bool(rights.get("license"))
        and bool(rights.get("holder"))
        and check_rights_public_export(quote).passed
    )


def _embedding_text(quote: dict[str, Any]) -> str:
    tags = " ".join(str(tag) for tag in quote.get("tags") or [])
    return "\n".join(
        part for part in (quote.get("text", ""), quote.get("section", ""), tags, quote.get("teaches", "")) if part
    )


@dataclass(frozen=True)
class IndexSnapshot:
    digest: str
    quotes: tuple[dict[str, Any], ...]
    vectors: tuple[list[float], ...]
    build_seconds: float


class RetrievalService:
    """Thread-safe, digest-keyed, in-memory index over eligible quotes."""

    def __init__(
        self,
        source: Path = DEFAULT_SOURCE,
        embed: Callable[[str], list[float]] = _ollama_embed,
    ) -> None:
        self.source = Path(source)
        self.embed = embed
        self._snapshot: IndexSnapshot | None = None
        self._lock = threading.Lock()

    def _read(self) -> tuple[bytes, dict[str, Any]]:
        raw = self.source.read_bytes()
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ValueError("TTOD source must contain a mapping")
        return raw, data

    def refresh(self) -> IndexSnapshot:
        raw, data = self._read()
        digest = hashlib.sha256(raw).hexdigest()
        with self._lock:
            if self._snapshot is not None and self._snapshot.digest == digest:
                return self._snapshot
            started = time.perf_counter()
            quotes = tuple(dict(q) for q in data.get("quotes", []) if isinstance(q, dict) and _is_public_active(q))
            vectors = tuple(self.embed(_embedding_text(quote)) for quote in quotes)
            self._snapshot = IndexSnapshot(digest, quotes, vectors, time.perf_counter() - started)
            return self._snapshot

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        context_tag: str | None = None,
        section: str | None = None,
    ) -> dict[str, Any]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if not 1 <= top_k <= 50:
            raise ValueError("top_k must be between 1 and 50")
        snapshot = self.refresh()
        query_vector = self.embed(query)
        ranked = []
        for quote, vector in zip(snapshot.quotes, snapshot.vectors):
            if section and quote.get("section") != section:
                continue
            if context_tag and context_tag not in (quote.get("tags") or []):
                continue
            ranked.append((_cosine(query_vector, vector), quote))
        ranked.sort(key=lambda pair: (-pair[0], str(pair[1].get("id", ""))))
        results = [
            {
                "id": quote.get("id"),
                "text": quote.get("text"),
                "section": quote.get("section"),
                "tags": quote.get("tags") or [],
                "origin": quote.get("origin"),
                "score": score,
            }
            for score, quote in ranked[:top_k]
        ]
        return {"results": results, "indexDigest": snapshot.digest, "indexedQuotes": len(snapshot.quotes)}

    def graph_neighborhood(
        self,
        quote_id: str | None = None,
        tag: str | None = None,
        section: str | None = None,
    ) -> dict[str, Any]:
        if not any((quote_id, tag, section)):
            raise ValueError("quote_id, tag, or section is required")
        _raw, data = self._read()
        eligible = [q for q in data.get("quotes", []) if isinstance(q, dict) and _is_public_active(q)]
        exporter = Exporter()
        nodes = exporter._graph_nodes(eligible)
        by_id = {q.get("id"): q for q in eligible}
        edges = [
            edge
            for edge in exporter._graph_edges(eligible)
            if edge.get("source") in by_id and edge.get("target") in by_id
        ]
        seeds = {
            q.get("id")
            for q in eligible
            if (quote_id and q.get("id") == quote_id)
            or (tag and tag in (q.get("tags") or []))
            or (section and q.get("section") == section)
        }
        if quote_id and quote_id not in by_id:
            return {"nodes": [], "edges": [], "seedIds": []}
        selected = set(seeds)
        for edge in edges:
            if edge.get("source") in seeds or edge.get("target") in seeds:
                selected.update((edge.get("source"), edge.get("target")))
        selected.discard(None)
        return {
            "nodes": [node for node in nodes if node.get("id") in selected],
            "edges": [edge for edge in edges if edge.get("source") in selected and edge.get("target") in selected],
            "seedIds": sorted(seeds),
        }


service = RetrievalService()


def semantic_retrieval(query: str, top_k: int = 5, contextTag: str | None = None, section: str | None = None) -> dict[str, Any]:
    """Return top-k semantic matches with cosine scores and unmodified provenance."""
    return service.semantic_search(query, top_k, contextTag, section)


def graph_neighborhood(quoteId: str | None = None, tag: str | None = None, section: str | None = None) -> dict[str, Any]:
    """Return the eligible TTOD graph induced by a quote, tag, or section."""
    return service.graph_neighborhood(quoteId, tag, section)


def index_status() -> dict[str, Any]:
    """Build or refresh the index and report its digest, size, and build time."""
    snapshot = service.refresh()
    return {"indexDigest": snapshot.digest, "indexedQuotes": len(snapshot.quotes), "buildSeconds": snapshot.build_seconds}


def create_mcp() -> Any:
    from fastmcp import FastMCP

    app = FastMCP("TTOD Oracle Retrieval")
    app.tool(semantic_retrieval)
    app.tool(graph_neighborhood)
    app.tool(index_status)
    return app


if __name__ == "__main__":
    create_mcp().run(transport="http", host="0.0.0.0", port=3001)
