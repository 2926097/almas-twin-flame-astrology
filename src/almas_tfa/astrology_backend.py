from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class NatalRequest:
    """Solicitud normalizada para un cálculo natal."""

    subject_id: str
    birth_date: str
    birth_time: str | None
    timezone: str | None
    place: str | None
    latitude: float | None
    longitude: float | None
    time_reliability: str | None

    @property
    def timed(self) -> bool:
        return bool(self.birth_time and self.timezone and self.location_available)

    @property
    def location_available(self) -> bool:
        return (
            self.place is not None
            or (self.latitude is not None and self.longitude is not None)
        )


class AstrologyBackend(Protocol):
    """Contrato mínimo para un motor astronómico/astrológico sustituible."""

    backend_id: str
    backend_version: str

    def calculate_natal(self, request: NatalRequest) -> Mapping[str, Any]:
        """Devuelve una carta natal normalizada para el sujeto."""
        ...


def natal_request_from_subject(subject: Mapping[str, Any]) -> NatalRequest:
    """Normaliza un subject de raw-input sin inventar datos faltantes."""

    subject_id = str(subject.get("id") or "")
    birth_date = subject.get("birth_date")
    if not subject_id:
        raise ValueError("El subject necesita id.")
    if not isinstance(birth_date, str) or not birth_date:
        raise ValueError(f"{subject_id}: birth_date es obligatorio.")

    latitude = subject.get("latitude")
    longitude = subject.get("longitude")

    return NatalRequest(
        subject_id=subject_id,
        birth_date=birth_date,
        birth_time=subject.get("birth_time"),
        timezone=subject.get("timezone"),
        place=subject.get("place"),
        latitude=float(latitude) if isinstance(latitude, (int, float)) else None,
        longitude=float(longitude) if isinstance(longitude, (int, float)) else None,
        time_reliability=subject.get("time_reliability"),
    )
