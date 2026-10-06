"""Solicitudes congeladas del adaptador; no conservan referencias mutables."""
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class UniformCycleRequest:
    payload_json: str
    source_json: str

    def engine_payload(self):
        return json.loads(self.payload_json)

    def source(self):
        return json.loads(self.source_json)
