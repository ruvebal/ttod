"""
TTOD Canonicalization (Q2E)

TTOD-C14N-v1 canonical serialization and digest computation.

Implements the exact specification from contract §2.3:
1. Recursively normalize every string to Unicode NFC
2. Reject non-string identifiers/tags and non-finite numbers
3. Emit UTF-8 JSON with lexicographically sorted keys, preserved array order, compact separators, one terminal newline
4. Compute SHA-256 over canonical quote projection → content_digest
5. Compute snapshot digest over quotes sorted by canonical ID, plus schema/taxonomy/collection policy versions
6. Record algorithm, projection version, source-file digest, record count, export options, and lifecycle states in manifest
"""

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union

import unicodedata


class CanonicalizationError(Exception):
    """Raised when canonicalization encounters invalid data that cannot be silently coerced."""


@dataclass
class ExportPolicy:
    """Policy for which records to include in an export."""

    include_deprecated: bool = True
    include_erased: bool = False
    include_restricted: bool = False
    public_export: bool = False

    def should_include(self, record: Dict[str, Any]) -> bool:
        """Determine if a record should be included based on its lifecycle/rights state."""
        status = record.get("status", "active")
        rights = record.get("rights", {})
        access = rights.get("access") if isinstance(rights, dict) else None

        # Erased records are never included unless explicitly requested
        if status == "erased" and not self.include_erased:
            return False

        # Deprecated records can be excluded
        if status == "deprecated" and not self.include_deprecated:
            return False

        # Public export excludes restricted records
        if self.public_export and access == "restricted":
            return False

        return True


@dataclass
class SnapshotManifest:
    """Manifest for a TTOD snapshot."""

    algorithm: str = "TTOD-C14N-v1"
    projection_version: str = "3.0.0"
    source_file_digest: str = ""
    record_count: int = 0
    export_options: Dict[str, Any] = field(default_factory=dict)
    included_lifecycle_states: List[str] = field(default_factory=list)
    excluded_lifecycle_states: List[str] = field(default_factory=list)
    snapshot_digest: str = ""
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "algorithm": self.algorithm,
            "projection_version": self.projection_version,
            "source_file_digest": self.source_file_digest,
            "record_count": self.record_count,
            "export_options": self.export_options,
            "included_lifecycle_states": self.included_lifecycle_states,
            "excluded_lifecycle_states": self.excluded_lifecycle_states,
            "snapshot_digest": self.snapshot_digest,
            "generated_at": self.generated_at,
        }


class Canonicalizer:
    """TTOD-C14N-v1 canonicalizer."""

    def __init__(self):
        self._identifier_keys: Set[str] = {"id", "proposal_id", "reviewer_id", "activity_id"}
        self._tag_keys: Set[str] = {"tags"}

    def normalize_string(self, s: str) -> str:
        """Normalize a string to Unicode NFC."""
        return unicodedata.normalize("NFC", s)

    def normalize_recursively(self, obj: Any) -> Any:
        """
        Recursively normalize an object to canonical form.

        Rules:
        - Strings: normalize to NFC
        - Identifiers (id, tags): must be strings, reject non-strings
        - Numbers: must be finite, reject NaN/Infinity
        - Objects: keys sorted lexicographically
        - Arrays: order preserved
        """
        if isinstance(obj, str):
            return self.normalize_string(obj)

        if isinstance(obj, dict):
            # Check for identifier keys that must be strings
            for key in self._identifier_keys:
                if key in obj and not isinstance(obj[key], str):
                    raise CanonicalizationError(
                        f"Identifier field '{key}' must be a string, got {type(obj[key]).__name__}"
                    )

            # Check for tag keys that must be strings
            for key in self._tag_keys:
                if key in obj:
                    tags = obj[key]
                    if isinstance(tags, list):
                        for i, tag in enumerate(tags):
                            if not isinstance(tag, str):
                                raise CanonicalizationError(
                                    f"Tag at index {i} must be a string, got {type(tag).__name__}"
                                )

            # Recursively normalize values and sort keys
            normalized = {}
            for key in sorted(obj.keys()):
                normalized[key] = self.normalize_recursively(obj[key])
            return normalized

        if isinstance(obj, list):
            # Recursively normalize items, preserving order
            return [self.normalize_recursively(item) for item in obj]

        if isinstance(obj, (int, float)):
            # Reject non-finite numbers
            if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                raise CanonicalizationError(f"Non-finite number not allowed: {obj}")
            return obj

        if obj is None or isinstance(obj, bool):
            return obj

        raise CanonicalizationError(f"Unsupported type for canonicalization: {type(obj).__name__}")

    def to_canonical_json(self, obj: Any) -> bytes:
        """
        Convert an object to canonical UTF-8 JSON bytes.

        Rules:
        - Lexicographically sorted object keys
        - Preserved array order
        - Compact separators (no whitespace)
        - Exactly one terminal newline
        """
        normalized = self.normalize_recursively(obj)
        json_str = json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return (json_str + "\n").encode("utf-8")

    def compute_content_digest(self, quote: Dict[str, Any]) -> str:
        """
        Compute SHA-256 digest over the canonical quote projection.

        The projection includes all fields except the digest fields themselves.
        """
        # Remove digest fields from projection
        projection = {k: v for k, v in quote.items() if k not in {"content_digest", "evidence_snapshot_digest", "wpl_record_digest"}}
        canonical_bytes = self.to_canonical_json(projection)
        return hashlib.sha256(canonical_bytes).hexdigest()

    def compute_snapshot_digest(
        self,
        quotes: List[Dict[str, Any]],
        schema_version: str,
        taxonomy_digest: str,
        collection_policy_digest: str,
    ) -> str:
        """
        Compute snapshot digest over ID-sorted quotes plus policy versions.

        The snapshot digest covers:
        - Quotes sorted by canonical ID
        - Schema version
        - Taxonomy digest
        - Collection policy digest
        """
        # Sort quotes by ID
        sorted_quotes = sorted(quotes, key=lambda q: q.get("id", ""))

        # Build snapshot object
        snapshot = {
            "schema_version": schema_version,
            "taxonomy_digest": taxonomy_digest,
            "collection_policy_digest": collection_policy_digest,
            "quotes": sorted_quotes,
        }

        canonical_bytes = self.to_canonical_json(snapshot)
        return hashlib.sha256(canonical_bytes).hexdigest()

    def compute_source_digest(self, source_bytes: bytes) -> str:
        """Compute SHA-256 digest of source file bytes."""
        return hashlib.sha256(source_bytes).hexdigest()

    def compute_taxonomy_digest(self, tag_taxonomy: Dict[str, Any]) -> str:
        """Compute digest of the tag taxonomy for snapshot inclusion."""
        canonical_bytes = self.to_canonical_json(tag_taxonomy)
        return hashlib.sha256(canonical_bytes).hexdigest()

    def compute_collection_policy_digest(self, collections: Dict[str, Any]) -> str:
        """Compute digest of collection policy for snapshot inclusion."""
        canonical_bytes = self.to_canonical_json(collections)
        return hashlib.sha256(canonical_bytes).hexdigest()

    def create_manifest(
        self,
        source_digest: str,
        record_count: int,
        export_policy: ExportPolicy,
        snapshot_digest: str,
        schema_version: str = "3.0.0",
        generated_at: Optional[str] = None,
    ) -> SnapshotManifest:
        """Create a snapshot manifest."""
        if generated_at is None:
            from datetime import datetime, timezone
            generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        manifest = SnapshotManifest(
            source_file_digest=source_digest,
            record_count=record_count,
            export_options={
                "include_deprecated": export_policy.include_deprecated,
                "include_erased": export_policy.include_erased,
                "include_restricted": export_policy.include_restricted,
                "public_export": export_policy.public_export,
            },
            included_lifecycle_states=["active"],
            excluded_lifecycle_states=[],
            snapshot_digest=snapshot_digest,
            generated_at=generated_at,
        )

        if export_policy.include_deprecated:
            manifest.included_lifecycle_states.append("deprecated")
        else:
            manifest.excluded_lifecycle_states.append("deprecated")

        if export_policy.include_erased:
            manifest.included_lifecycle_states.append("erased")
        else:
            manifest.excluded_lifecycle_states.append("erased")

        return manifest

    def verify_content_digest(self, quote: Dict[str, Any]) -> str:
        """
        Recompute TTOD-C14N-v1 content_digest and reject tampering.

        Returns the expected digest. Raises CanonicalizationError if the stored
        digest is present and does not match.
        """
        expected = self.compute_content_digest(quote)
        stored = quote.get("content_digest")
        if stored is not None and stored.lower() != expected:
            raise CanonicalizationError(
                f"content_digest tampering detected: stored {stored} != expected {expected}"
            )
        return expected
