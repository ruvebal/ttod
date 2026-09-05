from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Protocol

import httpx
from fastmcp import Client

from ttod_core.proposals import create_proposal
from ttod_core.repository import ProposalStore

from .config import Settings
from .models import OracleProposeRequest, OracleQueryPayload
from .storage import SnapshotService


GROUNDED_PROMPT = "Answer using only the supplied TTOD context. Cite relevant quote IDs. Respond in {language}."
CREATIVE_PROMPT = (
    "No strong match was found in the wisdom database for this query. Answer thoughtfully from general "
    "knowledge, but state plainly that this is not sourced from an existing TTOD quote. Respond in {language}."
)


def detect_language(text: str) -> str:
    lowered = f" {text.lower()} "
    spanish_markers = ("¿", "¡", " el ", " la ", " los ", " las ", " que ", " cómo ", " por qué ", " para ", " una ")
    return "es" if any(marker in lowered for marker in spanish_markers) else "en"


class OllamaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _require_model(self) -> str:
        if not self.settings.ollama_model:
            raise RuntimeError("OLLAMA_MODEL must name an installed local model")
        return self.settings.ollama_model

    async def ensure_model(self, client: httpx.AsyncClient, model: str | None = None) -> str:
        model = model or self._require_model()
        response = await client.get(f"{self.settings.ollama_base_url}/api/tags")
        response.raise_for_status()
        installed = {item.get("name") for item in response.json().get("models", [])}
        if model not in installed and not any(name and name.split(":")[0] == model for name in installed):
            raise RuntimeError(f"Configured Ollama model is not installed: {model}")
        return model

    async def generate(self, prompt: str, system: str) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=None) as client:
            await self.ensure_model(client)
            async with client.stream("POST", f"{self.settings.ollama_base_url}/api/generate", json={
                "model": self.settings.ollama_model, "prompt": prompt, "system": system, "stream": True,
            }) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        segment = json.loads(line).get("response", "")
                        if segment:
                            yield segment


class RetrievalClient(Protocol):
    async def semantic_retrieval(
        self, query: str, *, top_k: int, context_tag: str | None, section: str | None
    ) -> dict[str, Any]: ...


class FastMCPRetrievalClient:
    """Fail-closed Streamable HTTP adapter for R2's semantic_retrieval tool."""

    def __init__(self, server_url: str):
        self.endpoint = f"{server_url.rstrip('/')}/mcp"

    async def semantic_retrieval(
        self, query: str, *, top_k: int, context_tag: str | None, section: str | None
    ) -> dict[str, Any]:
        arguments = {"query": query, "top_k": top_k, "contextTag": context_tag, "section": section}
        try:
            async with Client(self.endpoint, timeout=30) as client:
                result = await client.call_tool("semantic_retrieval", arguments)
        except Exception as exc:
            raise RuntimeError(f"MCP semantic retrieval unavailable at {self.endpoint}: {exc}") from exc

        payload = result.structured_content or result.data
        if payload is None and result.content:
            text = getattr(result.content[0], "text", None)
            if text:
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise RuntimeError("MCP semantic_retrieval returned non-JSON text") from exc
        return normalize_retrieval_envelope(payload)


def normalize_retrieval_envelope(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise RuntimeError("MCP semantic_retrieval returned no structured object")
    results = payload.get("results")
    if not isinstance(results, list) or not isinstance(payload.get("indexDigest"), str) or not isinstance(payload.get("indexedQuotes"), int):
        raise RuntimeError("MCP semantic_retrieval envelope does not match the R2 contract")
    required = {"id", "text", "section", "tags", "origin", "score"}
    if any(not isinstance(item, dict) or not required.issubset(item) for item in results):
        raise RuntimeError("MCP semantic_retrieval result item does not match the R2 contract")
    return {"results": results, "indexDigest": payload["indexDigest"], "indexedQuotes": payload["indexedQuotes"]}


class OracleService:
    def __init__(
        self,
        settings: Settings,
        snapshots: SnapshotService,
        client: OllamaClient | None = None,
        retrieval_client: RetrievalClient | None = None,
    ):
        self.settings = settings
        self.snapshots = snapshots
        self.client = client or OllamaClient(settings)
        self.retrieval_client = retrieval_client or FastMCPRetrievalClient(settings.mcp_server_url)

    async def retrieve(self, query: str, context_tag: str | None = None) -> dict[str, Any]:
        return await self.retrieval_client.semantic_retrieval(
            query, top_k=self.settings.retrieval_top_k, context_tag=context_tag, section=None
        )

    async def stream(self, payload: OracleQueryPayload) -> AsyncIterator[bytes]:
        retrieval = await self.retrieve(payload.query, payload.contextTag)
        ranked = retrieval["results"]
        grounded = bool(ranked and ranked[0]["score"] >= self.settings.retrieval_threshold)
        mode = "grounded" if grounded else "creative"
        language = detect_language(payload.query)
        cited = [quote["id"] for quote in ranked] if grounded else None
        context = "\n".join(f"[{q['id']}] {q['text']}" for q in ranked)
        prompt = f"Conversation: {' | '.join(payload.sessionHistory)}\nQuestion: {payload.query}\nTTOD context:\n{context}"
        system = (GROUNDED_PROMPT if grounded else CREATIVE_PROMPT).format(language=language)
        async for text in self.client.generate(prompt, system):
            envelope = {"mode": mode, "text": text}
            if cited is not None:
                envelope["citedQuoteIds"] = cited
            yield f"data: {json.dumps(envelope, ensure_ascii=False)}\n\n".encode()

    async def propose(self, payload: OracleProposeRequest) -> dict[str, Any]:
        retrieval = await self.retrieve(payload.query)
        ranked = retrieval["results"]
        nearest = ranked[0] if ranked else None
        section = payload.suggestedSection or (nearest["section"] if nearest else "wisdom")
        tags = payload.suggestedTags if payload.suggestedTags is not None else (nearest.get("tags", []) if nearest else [])
        lang = detect_language(payload.creativeAnswer)
        candidate = {
            "text": payload.creativeAnswer,
            "section": section,
            "level": nearest.get("level", "intermediate") if nearest else "intermediate",
            "tags": tags,
            "teaches": payload.query,
            "origin": "blackbox",
            "lang": lang,
            "rights": {"access": "unresolved"},
            "source_refs": [{
                "kind": "oracle-creative-exchange", "query": payload.query,
                "mode": "creative", "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }
        proposal = create_proposal(candidate, "model", self.settings.ollama_model, "oracle-creative-mode")
        path = ProposalStore(self.settings.proposal_dir).save(proposal)
        result = proposal.to_dict()
        result["stored_at"] = str(path)
        return result
