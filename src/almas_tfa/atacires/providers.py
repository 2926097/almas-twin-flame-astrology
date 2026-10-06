"""Frontera reservada para técnicas con efemérides; el ciclo uniforme no la necesita."""
from datetime import datetime
from typing import Mapping, Protocol, runtime_checkable

@runtime_checkable
class EphemerisProvider(Protocol):
    backend_id: str
    backend_version: str
    provenance: Mapping
    def calculate_transit_positions(self, instant_utc: datetime) -> Mapping: ...
