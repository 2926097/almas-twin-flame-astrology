"""Fail-closed, offline readiness gate before starting ALMAS private loopback.

This does not certify the external golden reference gates or calculate any natal.
It confirms the explicitly selected local JPL kernel and pinned Moira package.
"""
from __future__ import annotations

from hashlib import sha256
from importlib import metadata
from pathlib import Path
import re
from typing import Callable

EXPECTED_MOIRA = "6.8.2"
ALLOWED_FAMILIES = frozenset(("DE430", "DE440", "DE441"))
SHA_PATTERN = re.compile(r"[a-f0-9]{64}\Z")


class LocalAstronomyNotReady(ValueError):
    """Stable error code, safe to display without leaking local paths."""


def assess_local_astronomy_runtime(
    kernel_path: str | Path, kernel_sha256: str, kernel_family: str,
    house_system: str, *,
    provider_version: Callable[[str], str] = metadata.version,
) -> dict[str, object]:
    if kernel_family not in ALLOWED_FAMILIES:
        raise LocalAstronomyNotReady("UNSUPPORTED_KERNEL_FAMILY")
    if not isinstance(kernel_sha256, str) or not SHA_PATTERN.fullmatch(kernel_sha256):
        raise LocalAstronomyNotReady("KERNEL_SHA256_INVALID")
    if house_system != "PLACIDUS":
        # The independent golden-house reference currently certifies Placidus.
        raise LocalAstronomyNotReady("HOUSE_SYSTEM_NOT_CERTIFIED_BY_GOLDEN_GATE")
    path = Path(kernel_path)
    if not path.is_file():
        raise LocalAstronomyNotReady("KERNEL_FILE_NOT_FOUND")
    try:
        digest = sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as exc:
        raise LocalAstronomyNotReady("KERNEL_UNREADABLE") from exc
    if digest.hexdigest() != kernel_sha256:
        raise LocalAstronomyNotReady("KERNEL_SHA256_MISMATCH")
    try:
        version = provider_version("moira-astro")
    except metadata.PackageNotFoundError as exc:
        raise LocalAstronomyNotReady("MOIRA_MISSING") from exc
    if version != EXPECTED_MOIRA:
        raise LocalAstronomyNotReady("MOIRA_VERSION_MISMATCH")
    # No personal birth data, kernel absolute path or secrets in this output.
    return {
        "state": "LOCAL_RUNTIME_READY",
        "backend": "MOIRA_JPL_SPK",
        "provider_version": EXPECTED_MOIRA,
        "kernel_family": kernel_family,
        "kernel_sha256": kernel_sha256,
        "house_system": house_system,
        "external_golden_gate": "NOT_VERIFIED_BY_THIS_PREFLIGHT",
        "private_remote_execution": False,
    }
