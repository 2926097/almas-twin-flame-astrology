from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class CalculationOptions:
    """Opciones declaradas para hacer reproducible un cálculo astrológico."""

    zodiac: str = "tropical"
    house_system: str | None = "topocentric"
    node_type: str = "true"
    position_mode: str | None = None
    coordinate_frame: str = "geocentric"
    ephemeris: str | None = None
    deep_audit: bool = False


@dataclass(frozen=True)
class BackendWarning:
    code: str
    message: str
    field: str | None = None
    severity: str = "WARNING"


def stable_fingerprint(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return value


def make_backend_envelope(
    *,
    request: Any,
    result: Mapping[str, Any],
    backend_id: str,
    backend_version: str,
    options: CalculationOptions | Mapping[str, Any] | None = None,
    warnings: Sequence[BackendWarning | Mapping[str, Any]] = (),
    engine_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Crea un contrato JSON estable alrededor de un resultado de cálculo."""

    if not backend_id or not backend_version:
        raise ValueError("backend_id y backend_version son obligatorios.")

    normalized_options = (
        asdict(options)
        if isinstance(options, CalculationOptions)
        else dict(options or {})
    )
    normalized_warnings = [
        asdict(item) if isinstance(item, BackendWarning) else dict(item)
        for item in warnings
    ]
    body = {
        "schema_version": "almas.astrology.backend.v1",
        "request": _jsonable(request),
        "calculation_options": normalized_options,
        "result": dict(result),
        "warnings": normalized_warnings,
        "engine": {
            "id": backend_id,
            "version": backend_version,
            **dict(engine_metadata or {}),
        },
    }
    return {**body, "payload_fingerprint": stable_fingerprint(body)}


def make_backend_error(
    *,
    code: str,
    message: str,
    backend_id: str,
    backend_version: str,
    field: str | None = None,
    candidates: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    if not code or not message:
        raise ValueError("code y message son obligatorios.")
    body = {
        "schema_version": "almas.astrology.backend.error.v1",
        "error": {
            "code": code,
            "message": message,
            "field": field,
            "candidates": [dict(item) for item in candidates],
        },
        "engine": {"id": backend_id, "version": backend_version},
    }
    return {**body, "payload_fingerprint": stable_fingerprint(body)}
