"""Deny-by-default personal-data firewall for ALMAS experimental API.

This is not an authentication/consent solution. No route calls it. A future
personal-data service must be a separately reviewed and approved architecture.
"""
from __future__ import annotations

class PersonalAnalysisDisabled(PermissionError):
    pass

PERSONAL_ANALYSIS_ENABLED = False

def require_personal_processing_allowed(*_args, **_kwargs) -> None:
    """Intentionally refuse every personal-case request, regardless of flags."""
    raise PersonalAnalysisDisabled("PRIVATE_ANALYSIS_NOT_ENABLED")
