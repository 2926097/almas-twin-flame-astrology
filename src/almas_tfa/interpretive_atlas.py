"""Atlas de autoría por referencias: sin cálculo, scoring ni prosa automática."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

# Sólo superficies analíticas; nunca raw_input, metadata o datos biográficos.
ROUTES = (
    "natal_context", "relationship_field", "draconic_context", "lots_context",
    "evidence", "semantic_motifs", "temporal", "ssar", "vedic",
    "natal", "structural_layers", "secondary_layers", "personal_temporal_complexes",
    "surrender_vestal", "counterevidence", "limitations", "source_trace", "doctrine",
    "data_quality", "coverage", "robustness",
)
PRIVATE_KEYS = {"metadata", "raw_input", "birth", "birth_date", "birth_time", "birthplace", "coordinates"}
DIMENSIONS = {
    "position": ("longitude", "sign", "degree_in_sign", "house", "declination", "speed", "retrograde"),
    "position_profile": ("longitude", "sign", "degree_in_sign", "house", "house_system", "decan", "sign_rulers", "dispositor_chains", "motion"),
    "contact": ("subject_a", "point_a", "subject_b", "point_b", "relation_id", "orb", "orb_limit", "layer_a", "layer_b"),
}


def _token(value: Any) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def resolve_pointer(canonical: Mapping[str, Any], pointer: str) -> Any:
    """Resolver JSON Pointer RFC 6901; conservar claves con / y ~."""
    if not pointer.startswith("/"):
        raise ValueError("Se exige un JSON Pointer absoluto.")
    current: Any = canonical
    for raw in pointer[1:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if not key.isdigit() or (len(key) > 1 and key.startswith("0")):
                raise ValueError("Índice de lista inválido.")
            current = current[int(key)]
        else:
            current = current[key]
    return current


def build_interpretive_atlas(canonical: Mapping[str, Any]) -> dict[str, Any]:
    """Indexar todos los campos autorizados, sin transformar coordenadas ni asignar significados.

    Los recuentos describen cobertura editorial, nunca raíces o independencia.
    Missing dimensions no implica que una técnica deba calcularse o que sea aplicable.
    """
    rows: list[dict[str, Any]] = []
    leaves: list[str] = []
    available: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, Mapping):
            kind = None
            if "point_id" in value and all(key in value for key in ("decan", "sign_rulers", "dispositor_chains", "motion")):
                kind = "position_profile"
            elif ("point_a" in value and "point_b" in value) or ("object_a" in value and "object_b" in value):
                kind = "contact"
            elif any(key in value for key in ("longitude", "sign", "degree_in_sign")):
                kind = "position"
            if kind:
                fields = sorted(key for key in value if key not in PRIVATE_KEYS)
                missing = [key for key in DIMENSIONS[kind] if value.get(key) is None or value.get(key) == ""]
                # Aspect y relation son variantes contractuales, no significados nuevos.
                if kind == "contact" and (value.get("aspect") or value.get("relation")) and "relation_id" in missing:
                    missing.remove("relation_id")
                if "object_a" in value:
                    # VED por signo/varga: no exigir longitud ni aspecto tropical.
                    missing = [key for key in ("varga_a", "varga_b", "sign_relation", "root_dependency_id") if value.get(key) is None]
                substrate_refs = []
                if kind == "contact" and "point_a" in value:
                    for endpoint in ("a", "b"):
                        subject, point = value.get("subject_"+endpoint), value.get("point_"+endpoint)
                        if subject and point:
                            for field in ("point_signs", "house_placements"):
                                ref = "/natal_context/subjects/" + _token(subject) + "/" + field + "/" + _token(point)
                                try:
                                    resolve_pointer(canonical, ref)
                                except (KeyError, IndexError, TypeError, ValueError):
                                    continue
                                substrate_refs.append(ref)
                rows.append(dict(kind=kind, data_ref=path,
                    field_refs=[path + "/" + _token(key) for key in fields],
                    natal_substrate_refs=substrate_refs,
                    missing_dimensions=missing))
            for key in sorted(value):
                if key not in PRIVATE_KEYS:
                    walk(value[key], path + "/" + _token(key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, path + "/" + str(index))
        else:
            leaves.append(path)

    for route in ROUTES:
        if canonical.get(route) is not None:
            available.append("/" + route)
            walk(canonical[route], "/" + route)
    fingerprint = sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
    return dict(atlas_version="ALMAS_INTERPRETIVE_ATLAS_V1", canonical_fingerprint=fingerprint,
        available_routes=available, missing_routes=["/"+r for r in ROUTES if canonical.get(r) is None],
        entries=rows, leaf_refs=leaves, canonical_values_embedded=False,
        canonical_values_mutated=False, creates_additional_evidence=False,
        semantic_interpretation_generated=False)


def audit_interpretive_coverage(canonical: Mapping[str, Any], atlas: Mapping[str, Any],
                                dispositions: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Control editorial estricto: cada objeto se desarrolla o excluye con motivo.

    INTERPRETED verifica la trazabilidad declarada, no la verdad de la interpretación.
    La ausencia de datos especializados debe explicarse sin inventarlos.
    """
    expected = build_interpretive_atlas(canonical)
    if atlas != expected:
        raise ValueError("Atlas alterado o fingerprint obsoleto; reconstruir desde el canónico.")
    allowed = {row["data_ref"] for row in atlas["entries"]}
    seen: set[str] = set()
    issues: list[str] = []
    for item in dispositions:
        ref = item.get("data_ref")
        if ref not in allowed or ref in seen:
            raise ValueError("Referencia desconocida o disposición duplicada.")
        seen.add(ref)
        if item.get("state") not in {"INTERPRETED", "EXCLUDED", "NOT_EVALUABLE"}:
            raise ValueError("Estado editorial inválido.")
        if not str(item.get("reason") or "").strip():
            issues.append(ref + ": falta explicación.")
        if item.get("state") == "INTERPRETED":
            for key in ("function", "dynamic", "alternative", "limits"):
                if not str(item.get(key) or "").strip():
                    issues.append(ref + ": falta " + key + ".")
            if item.get("epistemic_class") not in {"C_DOCTRINE", "D_CONTEMPORARY_USAGE", "E_PROJECT_HYPOTHESIS"}:
                issues.append(ref + ": clase interpretativa no declarada.")
            if item.get("epistemic_class") in {"C_DOCTRINE", "D_CONTEMPORARY_USAGE"} and not item.get("source_refs"):
                issues.append(ref + ": falta fuente/pasaje.")
    omitted = sorted(allowed - seen)
    return dict(state="COMPLETE" if not omitted and not issues else "PARTIAL",
        omitted_refs=omitted, issues=issues, total_entries=len(allowed),
        disposed_entries=len(seen), is_empirical_validation=False,
        is_ontological_discrimination=False)
