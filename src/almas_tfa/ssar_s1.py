"""Siete funciones S1 exploratorias sobre posiciones y raíces suministradas."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
from typing import Any, Mapping

from .ssar import run_ssar, validate_ssar_schema


def _load(name: str) -> dict:
    return json.loads(resources.files("almas_tfa").joinpath("data", name).read_text(encoding="utf-8"))


def load_s1_catalog() -> dict:
    """Conserva la procedencia nominal pendiente; no consulta fuentes en ejecución."""
    return _load("ssar-s1-catalog.json")


def load_s1_policy() -> dict:
    policy = _load("ssar-s1-development-policy.json")
    validate_ssar_schema(policy, "Policy")
    return policy


def s1_catalog_hash() -> str:
    encoded = json.dumps(load_s1_catalog(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def build_s1_request(request: Mapping[str, Any]) -> dict:
    """Añade fuentes auditadas; no rellena posiciones, precisión o anclajes ausentes."""
    validate_ssar_schema(request, "S1Request")
    if not request["enabled"]:
        return {"enabled": False}
    catalog = load_s1_catalog()
    registry = {entry["point_id"]: entry for entry in catalog["entries"]}
    appearances = []
    contacts_seen = set()
    for observation in request.get("observations", []):
        entry = registry[observation["point_id"]]
        geometry = observation["geometry"]
        if geometry is not None:
            signature = (observation["point_id"], geometry["target_id"], geometry["frame"],
                         float(geometry["longitude"]) % 360,
                         float(geometry["target_longitude"]) % 360,
                         tuple(sorted(observation["core_root_refs"])))
            if signature in contacts_seen:
                raise ValueError("El mismo contacto S1 requiere una aparición compartida.")
            contacts_seen.add(signature)
        appearances.append({
            **deepcopy(observation), "kind": "NAMED_SMALL_BODY",
            **{key: deepcopy(entry[key]) for key in ("provenance", "semantic_basis", "method")},
        })
    result = {"enabled": True, "sources": deepcopy(catalog["sources"]),
              "core_roots": deepcopy(request.get("core_roots", [])),
              "appearances": appearances, "units": deepcopy(request.get("units", [])),
              "edges": deepcopy(request.get("edges", []))}
    return result


def _reuse_contacts(request: Mapping, result: Mapping, catalog: Mapping) -> list[dict]:
    """Enlaza contactos upstream sin añadir apariciones, raíces ni unidades."""
    entries = {entry["point_id"]: entry for entry in catalog["entries"]}
    observations = {item["id"]: item for item in request.get("observations", [])}
    appearances = {item["id"]: item for item in result["appearances"]}
    seen, links = set(), []
    for record in request.get("existing_contacts", []):
        key = (record["layer"], record["evidence_id"])
        if key in seen:
            raise ValueError("Un contacto heredado sólo puede enlazarse una vez por capa.")
        seen.add(key)
        ref = record["appearance_ref"]
        if ref not in observations or record["layer"] not in entries[observations[ref]["point_id"]]["reuse_layers"]:
            raise ValueError("Referencia heredada rota o capa incompatible con S1.")
        observation = observations[ref]
        geometry = observation["geometry"]
        other = record["geometry"]
        if geometry is None or record["point_id"] != observation["point_id"]:
            raise ValueError("Un contacto heredado exige identidad y geometría disponibles.")
        if geometry["frame"] != other["frame"] or geometry["target_id"] != other["target_id"] or any(
            float(geometry[field]) % 360 != float(other[field]) % 360
            for field in ("longitude", "target_longitude")
        ):
            raise ValueError("El contacto heredado no reproduce la geometría suministrada.")
        if set(record["core_root_refs"]) != set(observation["core_root_refs"]):
            raise ValueError("El contacto heredado no reproduce los anclajes suministrados.")
        links.append({**deepcopy(record), "qualification": appearances[ref]["qualification"],
                      "contributes_new_evidence": False})
    return sorted(links, key=lambda item: (item["layer"], item["evidence_id"]))


def run_s1(request: Mapping[str, Any]) -> dict:
    """S1 optativo; no calcula efemérides ni invoca procesos temporales o M27."""
    if type(request.get("enabled")) is not bool:
        raise ValueError("S1 requiere enabled explícito.")
    # Igual que SSAR, la desactivación no exige extras ni inspecciona históricos.
    if not request["enabled"]:
        return {"schema_version": "ssar-s1-1.0-development", "catalog_id": None,
                "catalog_hash": None, "ssar": run_ssar({"enabled": False}),
                "functional_notes": [], "reused_contacts": []}
    effective_request = build_s1_request(request)
    policy, catalog = load_s1_policy(), load_s1_catalog()
    result = run_ssar(effective_request, policy=policy)
    registry = {entry["point_id"]: entry for entry in catalog["entries"]}
    notes = []
    for appearance in result["appearances"]:
        entry = registry[appearance["point_id"]]
        qualified = appearance["qualification"] in {"QUALIFIED_SIGNIFICATOR", "SECONDARY_SUPPORT"}
        notes.append({"appearance_ref": appearance["id"], "function_id": entry["function_id"],
                      "epistemic_class": "E_PROJECT_HYPOTHESIS",
                      "interpretation": entry["interpretation"] if qualified else None,
                      "inferential_limit": entry["inferential_limit"],
                      "source_refs": appearance["source_refs"],
                      "documentary_status": "NOT_EVALUABLE",
                      "reason": "M27_NOT_EVALUATED_IN_S1"})
    output = {"schema_version": "ssar-s1-1.0-development", "catalog_id": catalog["catalog_id"],
              "catalog_hash": s1_catalog_hash(), "ssar": result,
              "functional_notes": notes, "reused_contacts": _reuse_contacts(request, result, catalog)}
    validate_ssar_schema(output, "S1Result")
    return output


def validate_s1_result(result: Mapping, *, request: Mapping) -> None:
    """Reproduce la salida completa, incluidas fuentes, límites y enlaces heredados."""
    validate_ssar_schema(result, "S1Result")
    if result != run_s1(request):
        raise ValueError("La salida S1 no reproduce la entrada ni el catálogo efectivo.")
