"""
TTOD Validation Core (Q2V)

Strict validation and invariant engine for TTOD v3.

Implements JSON Schema validation plus invariants that JSON Schema alone cannot express:
- Global identity uniqueness
- Prefix/section match
- Root meta counts vs actual max-ID per section
- Tag taxonomy closure
- Collection and lesson reference integrity
- Related target resolution
- Lifecycle consistency
- Rights completeness for public-export-eligible records
- Review completeness (never count missing origin as human)
- Ancestry resolution
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from jsonschema import validate, ValidationError
except ImportError:
    raise ImportError("jsonschema not installed. Run: pip install jsonschema")


class DiagnosticCode(Enum):
    """Stable, enumerable diagnostic codes for validation errors and warnings."""

    # Schema-level errors (from Q1)
    MISSING_REVIEW = "MISSING_REVIEW"
    TYPE_ERROR = "TYPE_ERROR"
    NON_STRING_TAG = "NON_STRING_TAG"
    CANONICAL_ID_FORBIDDEN = "CANONICAL_ID_FORBIDDEN"

    # Q2V invariants
    DUPLICATE_ID = "DUPLICATE_ID"
    PREFIX_SECTION_MISMATCH = "PREFIX_SECTION_MISMATCH"
    META_COUNT_MISMATCH = "META_COUNT_MISMATCH"
    TAG_NOT_IN_TAXONOMY = "TAG_NOT_IN_TAXONOMY"
    COLLECTION_TARGET_NOT_FOUND = "COLLECTION_TARGET_NOT_FOUND"
    LESSON_TARGET_NOT_FOUND = "LESSON_TARGET_NOT_FOUND"
    RELATED_TARGET_NOT_FOUND = "RELATED_TARGET_NOT_FOUND"
    DEPRECATED_BY_NOT_FOUND = "DEPRECATED_BY_NOT_FOUND"
    SUPERSEDED_BY_NOT_FOUND = "SUPERSEDED_BY_NOT_FOUND"
    RIGHTS_INCOMPLETE_FOR_PUBLIC = "RIGHTS_INCOMPLETE_FOR_PUBLIC"
    ORIGIN_UNRESOLVED = "ORIGIN_UNRESOLVED"
    ANCESTRY_TARGET_NOT_FOUND = "ANCESTRY_TARGET_NOT_FOUND"
    ROOT_SOURCE_TARGET_NOT_FOUND = "ROOT_SOURCE_TARGET_NOT_FOUND"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"

    # Phase S S1′ — translation_of semantic invariants
    TRANSLATION_TARGET_UNRESOLVED = "TRANSLATION_TARGET_UNRESOLVED"
    TRANSLATION_TARGET_INACTIVE = "TRANSLATION_TARGET_INACTIVE"
    TRANSLATION_SAME_LANGUAGE = "TRANSLATION_SAME_LANGUAGE"
    TRANSLATION_SELF_TARGET = "TRANSLATION_SELF_TARGET"
    TRANSLATION_CHAIN = "TRANSLATION_CHAIN"
    TRANSLATION_DUPLICATE_ACTIVE = "TRANSLATION_DUPLICATE_ACTIVE"
    TRANSLATION_SECTION_MISMATCH = "TRANSLATION_SECTION_MISMATCH"


@dataclass
class Diagnostic:
    """A single validation diagnostic (error or warning)."""

    code: DiagnosticCode
    message: str
    path: str = ""
    quote_id: Optional[str] = None
    is_error: bool = True


@dataclass
class ValidationResult:
    """Result of validating a TTOD document."""

    is_valid: bool = True
    errors: List[Diagnostic] = field(default_factory=list)
    warnings: List[Diagnostic] = field(default_factory=list)

    def add_error(self, code: DiagnosticCode, message: str, path: str = "", quote_id: Optional[str] = None):
        self.errors.append(Diagnostic(code, message, path, quote_id, is_error=True))
        self.is_valid = False

    def add_warning(self, code: DiagnosticCode, message: str, path: str = "", quote_id: Optional[str] = None):
        self.warnings.append(Diagnostic(code, message, path, quote_id, is_error=False))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "is_valid": self.is_valid,
            "errors": [
                {
                    "code": d.code.value,
                    "message": d.message,
                    "path": d.path,
                    "quote_id": d.quote_id,
                }
                for d in self.errors
            ],
            "warnings": [
                {
                    "code": d.code.value,
                    "message": d.message,
                    "path": d.path,
                    "quote_id": d.quote_id,
                }
                for d in self.warnings
            ],
        }


def _compute_last_id_by_prefix(quotes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Max numeric suffix per ID prefix (matches live ttod.yml last_id_by_section keys)."""
    max_by_prefix: Dict[str, int] = {}
    for quote in quotes:
        quote_id = quote.get("id", "")
        if "-" not in quote_id:
            continue
        prefix, num_str = quote_id.split("-", 1)
        try:
            number = int(num_str)
        except ValueError:
            continue
        max_by_prefix[prefix] = max(max_by_prefix.get(prefix, 0), number)
    return max_by_prefix


class TTODValidator:
    """Strict TTOD v3 validator."""

    def __init__(self, schema_dir: Optional[Path] = None, strict: bool = False):
        """
        Initialize validator.

        Args:
            schema_dir: Directory containing JSON Schema files. Defaults to ../schema.
            strict: If True, all drift is a hard failure. If False, drift is a warning.
        """
        if schema_dir is None:
            schema_dir = Path(__file__).parent.parent / "schema"

        self.schema_dir = Path(schema_dir)
        self.strict = strict

        # Load schemas
        with open(self.schema_dir / "quote.schema.json") as f:
            self.quote_schema = json.load(f)
        with open(self.schema_dir / "ttod.schema.json") as f:
            self.ttod_schema = json.load(f)
        with open(self.schema_dir / "proposal.schema.json") as f:
            self.proposal_schema = json.load(f)

        # Inline quote schema for ttod root to avoid $ref resolution issues
        self.ttod_schema["properties"]["quotes"]["items"] = self.quote_schema

    def validate_quote(self, quote: Dict[str, Any]) -> ValidationResult:
        """Validate a single quote record."""
        result = ValidationResult()

        # JSON Schema validation
        try:
            validate(instance=quote, schema=self.quote_schema)
        except ValidationError as e:
            # Map schema errors to diagnostic codes
            code = self._map_schema_error_to_code(e)
            result.add_error(code, str(e), f"/{'/'.join(str(p) for p in e.path)}", quote.get("id"))

        # Q2V invariants
        self._validate_origin(quote, result)
        self._validate_digest(quote, result)

        return result

    def validate_root(self, root: Dict[str, Any]) -> ValidationResult:
        """Validate the entire TTOD root document."""
        result = ValidationResult()

        # JSON Schema validation
        try:
            validate(instance=root, schema=self.ttod_schema)
        except ValidationError as e:
            code = self._map_schema_error_to_code(e)
            result.add_error(code, str(e), f"/{'/'.join(str(p) for p in e.path)}")

        # Q2V invariants requiring full document context
        quotes = root.get("quotes", [])
        sections = root.get("sections", [])
        tag_taxonomy = root.get("tag_taxonomy", {})
        collections = root.get("collections", {})
        lessons = root.get("lessons", {})
        meta = root.get("meta", {})

        self._validate_identity_uniqueness(quotes, result)
        self._validate_prefix_section_match(quotes, sections, result)
        self._validate_meta_counts(quotes, meta, sections, result)
        self._validate_tag_taxonomy_closure(quotes, tag_taxonomy, result)
        self._validate_collection_integrity(collections, quotes, result)
        self._validate_lesson_integrity(lessons, quotes, result)
        self._validate_related_targets(quotes, result)
        self._validate_translation_of_edges(quotes, result)
        self._validate_lifecycle_consistency(quotes, result)
        self._validate_rights_completeness(quotes, result)
        self._validate_ancestry_resolution(quotes, result)

        # Per-quote invariants JSON Schema cannot express across the document
        for quote in quotes:
            self._validate_origin(quote, result)
            self._validate_digest(quote, result)

        # Convert warnings to errors in strict mode
        if self.strict and result.warnings:
            for warning in result.warnings:
                result.add_error(warning.code, warning.message, warning.path, warning.quote_id)
            result.warnings.clear()

        return result

    def validate_proposal(self, proposal: Dict[str, Any]) -> ValidationResult:
        """Validate a proposal record."""
        result = ValidationResult()

        # JSON Schema validation
        try:
            validate(instance=proposal, schema=self.proposal_schema)
        except ValidationError as e:
            code = self._map_schema_error_to_code(e)
            result.add_error(code, str(e), f"/{'/'.join(str(p) for p in e.path)}")

        return result

    def _map_schema_error_to_code(self, error: ValidationError) -> DiagnosticCode:
        """Map a JSON Schema ValidationError to a DiagnosticCode."""
        validator = error.validator
        instance = error.instance if hasattr(error, "instance") else {}
        path = [str(p) for p in error.path]
        message = error.message

        if validator == "not" and isinstance(instance, dict) and "id" in instance:
            return DiagnosticCode.CANONICAL_ID_FORBIDDEN
        if validator == "required":
            if "'validation'" in message:
                return DiagnosticCode.MISSING_REVIEW
            if "'origin'" in message:
                return DiagnosticCode.ORIGIN_UNRESOLVED
            if "'license'" in message or "'holder'" in message:
                return DiagnosticCode.RIGHTS_INCOMPLETE_FOR_PUBLIC
        if validator == "enum" and "origin" in path:
            return DiagnosticCode.ORIGIN_UNRESOLVED
        if validator == "type" and "tags" in path:
            return DiagnosticCode.NON_STRING_TAG
        if validator == "type":
            return DiagnosticCode.TYPE_ERROR

        return DiagnosticCode.TYPE_ERROR

    def _validate_origin(self, quote: Dict[str, Any], result: ValidationResult):
        """Validate origin field - never count missing as human."""
        origin = quote.get("origin")

        if origin is None:
            result.add_error(
                DiagnosticCode.ORIGIN_UNRESOLVED,
                "Origin field is missing; cannot infer as human",
                quote_id=quote.get("id"),
            )
        elif origin not in ["human", "studio", "blackbox", "mixed", "legacy-unknown"]:
            result.add_error(
                DiagnosticCode.ORIGIN_UNRESOLVED,
                f"Invalid origin value: {origin}",
                quote_id=quote.get("id"),
            )

    def _validate_digest(self, quote: Dict[str, Any], result: ValidationResult):
        """Validate digest format and recompute TTOD-C14N-v1 when a digest is present."""
        digest = quote.get("content_digest")
        if digest is None:
            return

        if not isinstance(digest, str) or len(digest) != 64 or not all(
            c in "0123456789abcdef" for c in digest.lower()
        ):
            result.add_error(
                DiagnosticCode.TYPE_ERROR,
                f"Invalid digest format: {digest}",
                quote_id=quote.get("id"),
            )
            return

        from ttod_core.canonical import CanonicalizationError, Canonicalizer

        try:
            expected = Canonicalizer().compute_content_digest(quote)
        except CanonicalizationError as exc:
            result.add_error(
                DiagnosticCode.TYPE_ERROR,
                f"Cannot recompute content digest: {exc}",
                quote_id=quote.get("id"),
            )
            return

        if digest.lower() != expected:
            result.add_error(
                DiagnosticCode.DIGEST_MISMATCH,
                f"content_digest does not match TTOD-C14N-v1 recomputation (expected {expected})",
                quote_id=quote.get("id"),
            )

    def _validate_identity_uniqueness(self, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate that all quote IDs are globally unique."""
        seen_ids: Set[str] = set()
        for quote in quotes:
            quote_id = quote.get("id")
            if quote_id in seen_ids:
                result.add_error(
                    DiagnosticCode.DUPLICATE_ID,
                    f"Duplicate quote ID: {quote_id}",
                    quote_id=quote_id,
                )
            seen_ids.add(quote_id)

    def _validate_prefix_section_match(self, quotes: List[Dict[str, Any]], sections: List[Dict[str, Any]], result: ValidationResult):
        """Validate that quote ID prefix matches section."""
        section_prefix_map = {s["id"]: s["prefix"] for s in sections}

        for quote in quotes:
            quote_id = quote.get("id", "")
            section = quote.get("section")

            if "-" in quote_id and section:
                prefix = quote_id.split("-")[0]
                expected_prefix = section_prefix_map.get(section)

                if expected_prefix and prefix != expected_prefix:
                    result.add_error(
                        DiagnosticCode.PREFIX_SECTION_MISMATCH,
                        f"Quote ID prefix '{prefix}' does not match section '{section}' (expected '{expected_prefix}')",
                        quote_id=quote_id,
                    )

    def _validate_meta_counts(
        self,
        quotes: List[Dict[str, Any]],
        meta: Dict[str, Any],
        sections: List[Dict[str, Any]],
        result: ValidationResult,
    ):
        """Validate that meta.last_id_by_section matches actual max ID per prefix."""
        last_id_by_section = meta.get("last_id_by_section", {})
        section_to_prefix = {s["id"]: s["prefix"] for s in sections}
        actual_max_by_prefix = _compute_last_id_by_prefix(quotes)

        for key, claimed_max in last_id_by_section.items():
            prefix = section_to_prefix.get(key, key)
            actual_max = actual_max_by_prefix.get(prefix, 0)
            if claimed_max != actual_max:
                message = (
                    f"meta.last_id_by_section['{key}'] claims {claimed_max}, "
                    f"but actual max ID for prefix '{prefix}' is {actual_max}"
                )
                if self.strict:
                    result.add_error(DiagnosticCode.META_COUNT_MISMATCH, message)
                else:
                    result.add_warning(DiagnosticCode.META_COUNT_MISMATCH, message)

    def _validate_tag_taxonomy_closure(self, quotes: List[Dict[str, Any]], tag_taxonomy: Dict[str, Any], result: ValidationResult):
        """Validate that every tag used by quotes exists in the declared taxonomy."""
        # Flatten taxonomy to a set of all declared tags
        declared_tags = set()
        for category, tags in tag_taxonomy.items():
            if isinstance(tags, list):
                declared_tags.update(tags)
            elif isinstance(tags, dict):
                declared_tags.update(tags.keys())

        for quote in quotes:
            tags = quote.get("tags", [])
            if not isinstance(tags, list):
                continue

            for tag in tags:
                if tag not in declared_tags:
                    if self.strict:
                        result.add_error(
                            DiagnosticCode.TAG_NOT_IN_TAXONOMY,
                            f"Tag '{tag}' not found in declared taxonomy",
                            quote_id=quote.get("id"),
                        )
                    else:
                        result.add_warning(
                            DiagnosticCode.TAG_NOT_IN_TAXONOMY,
                            f"Tag '{tag}' not found in declared taxonomy",
                            quote_id=quote.get("id"),
                        )

    def _validate_collection_integrity(self, collections: Dict[str, Any], quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate that collection IDs resolve to existing quotes."""
        quote_ids = {q.get("id") for q in quotes}

        for collection_name, collection in collections.items():
            if isinstance(collection, dict):
                collection_ids = collection.get("ids", [])
                for cid in collection_ids:
                    if cid not in quote_ids:
                        result.add_error(
                            DiagnosticCode.COLLECTION_TARGET_NOT_FOUND,
                            f"Collection '{collection_name}' references non-existent quote ID: {cid}",
                        )

    def _validate_lesson_integrity(self, lessons: Any, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate that lesson quote IDs resolve to existing quotes."""
        quote_ids = {q.get("id") for q in quotes}

        if isinstance(lessons, dict):
            items = lessons.items()
        elif isinstance(lessons, list):
            items = []
            for index, lesson in enumerate(lessons):
                if isinstance(lesson, dict):
                    name = lesson.get("id") or lesson.get("slug") or str(index)
                    items.append((name, lesson))
        else:
            return

        for lesson_name, lesson in items:
            if not isinstance(lesson, dict):
                continue
            lesson_ids = lesson.get("quote_ids") or lesson.get("ids") or []
            for lid in lesson_ids:
                if lid not in quote_ids:
                    result.add_error(
                        DiagnosticCode.LESSON_TARGET_NOT_FOUND,
                        f"Lesson '{lesson_name}' references non-existent quote ID: {lid}",
                    )

    def _validate_related_targets(self, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate that related targets resolve to existing quotes."""
        quote_ids = {q.get("id") for q in quotes}

        for quote in quotes:
            related = quote.get("related", [])
            if not isinstance(related, list):
                continue

            for rid in related:
                if rid not in quote_ids:
                    result.add_error(
                        DiagnosticCode.RELATED_TARGET_NOT_FOUND,
                        f"Quote '{quote.get('id')}' references non-existent related ID: {rid}",
                        quote_id=quote.get("id"),
                    )

    @staticmethod
    def _quote_status(quote: Dict[str, Any]) -> str:
        status = quote.get("status")
        return status if isinstance(status, str) and status else "active"

    @staticmethod
    def _outgoing_translation_targets(quote: Dict[str, Any]) -> List[str]:
        edges = quote.get("relation_edges") or []
        targets: List[str] = []
        if not isinstance(edges, list):
            return targets
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            if edge.get("relation_type") == "translation_of" and edge.get("target"):
                targets.append(str(edge["target"]))
        return targets

    def _validate_translation_of_edges(self, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Enforce Phase S translation_of semantic invariants (S0 decision 5)."""
        by_id: Dict[str, Dict[str, Any]] = {
            q["id"]: q for q in quotes if isinstance(q, dict) and q.get("id")
        }
        # (target_id, translator_lang) -> list of translator quote ids (active only)
        active_pairs: Dict[tuple, List[str]] = {}

        for quote in quotes:
            if not isinstance(quote, dict):
                continue
            quote_id = quote.get("id")
            for target_id in self._outgoing_translation_targets(quote):
                if target_id == quote_id:
                    result.add_error(
                        DiagnosticCode.TRANSLATION_SELF_TARGET,
                        f"Quote '{quote_id}' translation_of targets itself",
                        quote_id=quote_id,
                    )
                    continue

                target = by_id.get(target_id)
                if target is None:
                    result.add_error(
                        DiagnosticCode.TRANSLATION_TARGET_UNRESOLVED,
                        f"Quote '{quote_id}' translation_of references non-existent ID: {target_id}",
                        quote_id=quote_id,
                    )
                    continue

                if self._quote_status(target) != "active":
                    result.add_error(
                        DiagnosticCode.TRANSLATION_TARGET_INACTIVE,
                        f"Quote '{quote_id}' translation_of target '{target_id}' is not active "
                        f"(status={self._quote_status(target)!r})",
                        quote_id=quote_id,
                    )

                source_lang = quote.get("lang")
                target_lang = target.get("lang")
                if (
                    isinstance(source_lang, str)
                    and isinstance(target_lang, str)
                    and source_lang == target_lang
                ):
                    result.add_error(
                        DiagnosticCode.TRANSLATION_SAME_LANGUAGE,
                        f"Quote '{quote_id}' translation_of '{target_id}' has same lang={source_lang!r}",
                        quote_id=quote_id,
                    )

                # Star, not chain: target must not itself carry an outgoing translation_of.
                if self._outgoing_translation_targets(target):
                    result.add_error(
                        DiagnosticCode.TRANSLATION_CHAIN,
                        f"Quote '{quote_id}' translation_of '{target_id}' points at a translation "
                        f"(star topology required, not a chain)",
                        quote_id=quote_id,
                    )

                if (
                    self._quote_status(quote) == "active"
                    and isinstance(source_lang, str)
                    and source_lang
                ):
                    key = (target_id, source_lang)
                    active_pairs.setdefault(key, []).append(str(quote_id))

                source_section = quote.get("section")
                target_section = target.get("section")
                if (
                    isinstance(source_section, str)
                    and isinstance(target_section, str)
                    and source_section != target_section
                ):
                    result.add_warning(
                        DiagnosticCode.TRANSLATION_SECTION_MISMATCH,
                        f"Quote '{quote_id}' section={source_section!r} differs from "
                        f"translation_of target '{target_id}' section={target_section!r}",
                        quote_id=quote_id,
                    )

        for (target_id, lang), translators in active_pairs.items():
            if len(translators) > 1:
                result.add_error(
                    DiagnosticCode.TRANSLATION_DUPLICATE_ACTIVE,
                    f"Multiple active translations in lang={lang!r} of '{target_id}': {translators}",
                    quote_id=translators[0],
                )

    def _validate_lifecycle_consistency(self, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate lifecycle consistency (deprecated_by, superseded_by targets resolve)."""
        quote_ids = {q.get("id") for q in quotes}

        for quote in quotes:
            deprecated_by = quote.get("deprecated_by")
            if deprecated_by and deprecated_by not in quote_ids:
                result.add_error(
                    DiagnosticCode.DEPRECATED_BY_NOT_FOUND,
                    f"Quote '{quote.get('id')}' deprecated_by references non-existent ID: {deprecated_by}",
                    quote_id=quote.get("id"),
                )

            superseded_by = quote.get("superseded_by")
            if superseded_by and superseded_by not in quote_ids:
                result.add_error(
                    DiagnosticCode.SUPERSEDED_BY_NOT_FOUND,
                    f"Quote '{quote.get('id')}' superseded_by references non-existent ID: {superseded_by}",
                    quote_id=quote.get("id"),
                )

    def _validate_rights_completeness(self, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate rights completeness for records flagged public-export-eligible."""
        for quote in quotes:
            rights = quote.get("rights", {})
            access = rights.get("access") if isinstance(rights, dict) else None

            if access == "public":
                # Check for required rights fields
                if not isinstance(rights, dict):
                    result.add_error(
                        DiagnosticCode.RIGHTS_INCOMPLETE_FOR_PUBLIC,
                        f"Quote '{quote.get('id')}' has public access but missing rights object",
                        quote_id=quote.get("id"),
                    )
                else:
                    required_fields = ["license", "holder"]
                    for field in required_fields:
                        if not rights.get(field):
                            result.add_error(
                                DiagnosticCode.RIGHTS_INCOMPLETE_FOR_PUBLIC,
                                f"Quote '{quote.get('id')}' has public access but missing rights.{field}",
                                quote_id=quote.get("id"),
                            )

    def _validate_ancestry_resolution(self, quotes: List[Dict[str, Any]], result: ValidationResult):
        """Validate ancestry resolution (immediate_parent_refs, root_source_refs)."""
        quote_ids = {q.get("id") for q in quotes}

        for quote in quotes:
            immediate_parent_refs = quote.get("immediate_parent_refs", [])
            if isinstance(immediate_parent_refs, list):
                for ref in immediate_parent_refs:
                    if ref not in quote_ids:
                        result.add_error(
                            DiagnosticCode.ANCESTRY_TARGET_NOT_FOUND,
                            f"Quote '{quote.get('id')}' immediate_parent_refs references non-existent ID: {ref}",
                            quote_id=quote.get("id"),
                        )

            root_source_refs = quote.get("root_source_refs", [])
            if isinstance(root_source_refs, list):
                for ref in root_source_refs:
                    if ref not in quote_ids:
                        result.add_error(
                            DiagnosticCode.ROOT_SOURCE_TARGET_NOT_FOUND,
                            f"Quote '{quote.get('id')}' root_source_refs references non-existent ID: {ref}",
                            quote_id=quote.get("id"),
                        )
