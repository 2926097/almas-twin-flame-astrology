"""Contratos experimentales SSAR; API auxiliar sin conexión al scoring legacy."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
from math import isfinite
from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect

KINDS = ("NAMED_SMALL_BODY", "CALCULATED_POINT", "HELLENISTIC_LOT")
STATES = ("SUPPORTED", "COMPATIBLE", "INSUFFICIENT", "CONTRADICTED", "NOT_EVALUABLE")
CONTRACT_VERSION = "ssar-contract-1.0-development"


def load_ssar_policy() -> dict[str, Any]:
    path = resources.files("almas_tfa").joinpath("data", "ssar-development-policy.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _finite_tree(value: Any) -> None:
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("SSAR no admite valores numéricos no finitos.")
    if isinstance(value, Mapping):
        for item in value.values():
            _finite_tree(item)
    elif isinstance(value, list):
        for item in value:
            _finite_tree(item)


def validate_ssar_schema(value: Mapping[str, Any], definition: str) -> None:
    """Valida el contrato empaquetado; exige el extra schema-validation."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError("SSAR requiere el extra declarado schema-validation para validar contratos.") from exc
    path = resources.files("almas_tfa").joinpath("data", "ssar-contract-definitions.json")
    schema = json.loads(path.read_text(encoding="utf-8"))
    if definition not in schema["$defs"]:
        raise ValueError("Definición SSAR desconocida.")
    schema["$ref"] = "#/$defs/" + definition
    _finite_tree(value)
    Draft202012Validator(schema).validate(value)


def ssar_policy_hash(policy: Mapping[str, Any]) -> str:
    """SHA-256 de JSON UTF-8, claves ordenadas, sin espacios ni NaN."""
    validate_ssar_schema(policy, "Policy")
    encoded = json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _index(items: list[dict], field: str) -> dict[str, dict]:
    indexed = {item[field]: item for item in items}
    if len(indexed) != len(items):
        raise ValueError(f"Identificadores SSAR duplicados: {field}.")
    return indexed


def _references(refs: list[str], registry: Mapping, label: str) -> None:
    if set(refs) - set(registry):
        raise ValueError(f"Referencias SSAR rotas en {label}.")


def validate_ssar_request(request: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    validate_ssar_schema(request, "Request")
    validate_ssar_schema(policy, "Policy")
    for rule in policy["type_rules"].values():
        if len(rule["sample_offsets_minutes"]) < rule["minimum_samples"]:
            raise ValueError("La política de robustez tiene una rejilla insuficiente.")
    sources = _index(request.get("sources", []), "id")
    roots = _index(request.get("core_roots", []), "root_id")
    appearances = _index(request.get("appearances", []), "id")
    units = _index(request.get("units", []), "id")
    for root in roots.values():
        if root["core_eligible"] and not root["core_evidence_ids"]:
            raise ValueError("Una raíz core SSAR necesita core_evidence_ids heredados.")
    for appearance in appearances.values():
        for key in ("provenance", "semantic_basis", "method"):
            record = appearance[key]
            if record is not None:
                _references(record["source_refs"], sources, appearance["id"] + "/" + key)
        _references(appearance["core_root_refs"], roots, appearance["id"] + "/raíces")
        for root_id in appearance["core_root_refs"]:
            if not roots[root_id]["core_eligible"]:
                raise ValueError("Una referencia de anclaje SSAR debe señalar una raíz core.")
            geometry = appearance["geometry"]
            if geometry is not None and geometry["target_id"] not in roots[root_id]["point_ids"]:
                raise ValueError("El target del significador no pertenece a la raíz core referenciada.")
        robustness = appearance["robustness"]
        if robustness is not None:
            _index(robustness["samples"], "id")
            offsets = [sample["offset_minutes"] for sample in robustness["samples"]]
            if len(offsets) != len(set(offsets)):
                raise ValueError("Las perturbaciones SSAR tienen offsets duplicados.")
    for unit in units.values():
        _references([unit["appearance_ref"]], appearances, "unidad/" + unit["id"])
        if unit["technique"] not in policy["technique_groups"]:
            raise ValueError("La técnica no tiene grupo publicado en la política SSAR.")
    for edge in request.get("edges", []):
        _references([edge["a"], edge["b"]], units, "dependencia")
        if edge["a"] == edge["b"]:
            raise ValueError("Una dependencia SSAR requiere dos unidades distintas.")
        if edge["rule_id"] != policy["dependency_rules"][edge["relation"]]:
            raise ValueError("La dependencia no corresponde a una regla de política.")
        if edge["relation"] == "EQUIVALENT" and units[edge["a"]]["equivalence_key"] != units[edge["b"]]["equivalence_key"]:
            raise ValueError("La equivalencia declarada tiene claves distintas.")


def assess_ssar_claim(*, scope: str, policy_ref: str | None, rule_ref: str | None,
                      coverage_sufficient: bool, positive_complete: bool = False,
                      compatible: bool = False, mixed_or_underdetermined: bool = False,
                      evidence_refs: list[str] | None = None,
                      excluding_counterevidence_refs: list[str] | None = None,
                      counterevidence_evaluable: bool = False) -> dict[str, Any]:
    """Decide un alcance bajo criterios aportados; no verifica hechos externos."""
    flags = (coverage_sufficient, positive_complete, compatible, mixed_or_underdetermined, counterevidence_evaluable)
    if any(type(flag) is not bool for flag in flags):
        raise ValueError("Los criterios de estado SSAR deben ser booleanos explícitos.")
    if not isinstance(scope, str) or not scope:
        raise ValueError("El estado SSAR requiere alcance.")
    evidence = sorted(set(evidence_refs or []))
    counter = sorted(set(excluding_counterevidence_refs or []))
    if not policy_ref or not rule_ref:
        status, reason = "NOT_EVALUABLE", "POLICY_OR_RULE_MISSING"
    elif counter and counterevidence_evaluable:
        status, reason = "CONTRADICTED", "PREDEFINED_EXCLUDING_COUNTEREVIDENCE"
    elif not coverage_sufficient or (counter and not counterevidence_evaluable):
        status, reason = "NOT_EVALUABLE", "ESSENTIAL_COVERAGE_MISSING"
    elif mixed_or_underdetermined:
        status, reason = "INSUFFICIENT", "MIXED_OR_UNRESOLVED_ALTERNATIVES"
    elif positive_complete:
        status, reason = "SUPPORTED", "ALL_DEFINED_CONDITIONS_MET"
    elif compatible:
        status, reason = "COMPATIBLE", "COHERENT_BELOW_POSITIVE_CRITERION"
    else:
        status, reason = "INSUFFICIENT", "POSITIVE_CRITERION_NOT_MET"
    out = dict(scope=scope, status=status, policy_ref=policy_ref, rule_ref=rule_ref,
               evidence_refs=evidence, counterevidence_refs=counter,
               coverage_sufficient=coverage_sufficient, reason=reason)
    validate_ssar_schema(out, "Assessment")
    return out


def _source_quality(refs: list[str], sources: Mapping, policy: Mapping, scope: str) -> str:
    if not refs or any(sources[key]["verification_status"] != "VERIFIED" or scope not in sources[key]["claim_scopes"] for key in refs):
        return "MISSING"
    if any(sources[key]["priority"] not in policy["qualified_source_priorities"] for key in refs):
        return "EXPLORATORY"
    return "QUALIFIED"


def _appearance(appearance: dict, sources: Mapping, policy: Mapping) -> dict:
    point_rule = policy["point_rules"].get(appearance["point_id"])
    type_rule = policy["type_rules"][appearance["kind"]]
    reasons, weak = [], False
    rule_ref = point_rule["rule_id"] if point_rule else None
    source_refs = sorted({ref for field in ("provenance", "semantic_basis", "method")
                          for ref in (appearance[field] or {}).get("source_refs", [])})
    project_method = (appearance["method"] or {}).get("epistemic_class") == "E_PROJECT_HYPOTHESIS"
    out = dict(id=appearance["id"], point_id=appearance["point_id"],
               kind=appearance["kind"], function_id=point_rule["function_id"] if point_rule else None,
               epistemic_class=(appearance["semantic_basis"] or {}).get("epistemic_class"),
               qualification="BLOCKED", assessment=None, gate_reasons=[],
               core_root_refs=list(appearance["core_root_refs"]), source_refs=source_refs,
               matched_aspect=None, robustness=None, project_method=project_method)
    if point_rule is None:
        reasons.append("POINT_NOT_ENABLED_BY_POLICY")
    elif point_rule["kind"] != appearance["kind"]:
        raise ValueError("Tipo de aparición incompatible con la política del punto.")
    prov = appearance["provenance"]
    if prov is None or prov["identity_status"] != "VERIFIED":
        reasons.append("IDENTITY_NOT_VERIFIED")
    else:
        if appearance["kind"] == "NAMED_SMALL_BODY":
            if prov["basis"] == "TECHNICAL":
                reasons.append("NAMED_BODY_BASIS_NOT_DEFINED")
            elif prov["basis"] == "NAME":
                if prov["verification_status"] != "VERIFIED":
                    reasons.append("NAME_PROVENANCE_NOT_VERIFIED")
                elif prov["name_class"] not in {"NP1_MYTHIC_DIRECT", "NP2_CONCEPT_DIRECT"}:
                    reasons.append("NOMINAL_SEMANTIC_ASSOCIATION_FORBIDDEN")
        elif prov["basis"] != "TECHNICAL" or prov["verification_status"] != "VERIFIED" or not prov["algorithm"] or not prov["conventions"] or not prov["inputs"] or not prov["variant"]:
            reasons.append("TECHNICAL_PROVENANCE_INCOMPLETE")
        if type_rule["requires_sect"] and prov["sect"] not in {"DAY", "NIGHT"}:
            reasons.append("REQUIRED_SECT_UNRESOLVED")
        scope = {"NAME": "NAME_ORIGIN", "INDEPENDENT_OF_NAME": "IDENTITY", "TECHNICAL": "TECHNICAL_DEFINITION"}[prov["basis"]]
        quality = _source_quality(prov["source_refs"], sources, policy, scope)
        if quality == "MISSING":
            reasons.append("PROVENANCE_SOURCE_MISSING")
        weak |= quality == "EXPLORATORY"
    for field in ("semantic_basis", "method"):
        record = appearance[field]
        if record is None:
            reasons.append(field.upper() + "_UNDEFINED")
            continue
        scope = "SEMANTIC_BASIS" if field == "semantic_basis" else "ASTROLOGICAL_METHOD"
        quality = _source_quality(record["source_refs"], sources, policy, scope)
        if quality == "MISSING":
            reasons.append(field.upper() + "_SOURCE_MISSING")
        weak |= quality == "EXPLORATORY"
        if record["epistemic_class"] == "E_PROJECT_HYPOTHESIS":
            if not record["justification"] or record["policy_ref"] != policy["policy_id"]:
                reasons.append(field.upper() + "_PROJECT_JUSTIFICATION_MISSING")
        elif any(sources[key]["epistemic_class"] != record["epistemic_class"] for key in record["source_refs"]):
            reasons.append(field.upper() + "_SOURCE_CLASS_MISMATCH")
    if project_method and point_rule and not point_rule["allow_project_method"]:
        reasons.append("PROJECT_METHOD_NOT_AUTHORIZED")
    if prov and prov["basis"] == "INDEPENDENT_OF_NAME":
        method = appearance["method"]
        if method is None or not method["justification"]:
            reasons.append("NAME_INDEPENDENT_METHOD_UNDEFINED")
    geometry = appearance["geometry"]
    if geometry is None:
        reasons.append("GEOMETRY_MISSING")
    if type_rule["aspect_policy"] is None:
        reasons.append("GEOMETRY_POLICY_UNDEFINED")
    robust = appearance["robustness"]
    if robust is None or robust["input_precision_sufficient"] is not True:
        reasons.append("PRECISION_OR_ROBUSTNESS_MISSING")
    elif len(robust["samples"]) < type_rule["minimum_samples"]:
        reasons.append("ROBUSTNESS_SAMPLE_COVERAGE_INSUFFICIENT")
    elif {sample["offset_minutes"] for sample in robust["samples"]} != set(type_rule["sample_offsets_minutes"]):
        reasons.append("ROBUSTNESS_GRID_NOT_COVERED")
    if not appearance["core_anchor_search_complete"]:
        reasons.append("CORE_ANCHOR_COVERAGE_MISSING")
    if reasons:
        out["gate_reasons"] = sorted(set(reasons))
        out["assessment"] = assess_ssar_claim(scope="FUNCTIONAL_INTERPRETATION", policy_ref=policy["policy_id"], rule_ref=rule_ref, coverage_sufficient=False, evidence_refs=[appearance["id"]])
        return out
    aspect_policy = type_rule["aspect_policy"]
    match = match_declared_aspect(geometry["longitude"], geometry["target_longitude"], aspect_policy)
    out["matched_aspect"] = match
    if match is None:
        out["qualification"] = "NO_CONTACT"
        out["gate_reasons"] = ["NO_DECLARED_CONTACT"]
        out["assessment"] = assess_ssar_claim(scope="STRUCTURAL_GEOMETRY", policy_ref=policy["policy_id"], rule_ref=rule_ref, coverage_sufficient=True, excluding_counterevidence_refs=[appearance["id"]], counterevidence_evaluable=True)
        return out
    # Las perturbaciones deben conservar el mismo aspecto, no uno alternativo.
    matches = [match_declared_aspect(sample["longitude"], sample["target_longitude"], aspect_policy) for sample in robust["samples"]]
    preserved = sum(item is not None and item["aspect"] == match["aspect"] for item in matches)
    fraction = preserved / len(matches)
    out["robustness"] = {"rule_ref": type_rule["robustness_rule_id"], "sample_count": len(matches), "preserved_count": preserved, "preserved_fraction": fraction, "required_fraction": type_rule["minimum_preserved_fraction"]}
    if not appearance["core_root_refs"]:
        weak = True
        out["gate_reasons"].append("NO_CORE_ANCHOR_FOUND")
    if fraction < type_rule["minimum_preserved_fraction"]:
        weak = True
        out["gate_reasons"].append("ROBUSTNESS_BELOW_QUALIFICATION_CRITERION")
    if any(sources[key]["priority"] not in policy["qualified_source_priorities"] for key in source_refs):
        out["gate_reasons"].append("SOURCE_QUALITY_EXPLORATORY")
    out["qualification"] = "SECONDARY_SUPPORT" if weak else "QUALIFIED_SIGNIFICATOR"
    out["assessment"] = assess_ssar_claim(scope="FUNCTIONAL_INTERPRETATION", policy_ref=policy["policy_id"], rule_ref=rule_ref, coverage_sufficient=True, positive_complete=not weak, compatible=weak, evidence_refs=[appearance["id"]])
    return out


def _components(ids: list[str], pairs: list[tuple[str, str]]) -> list[list[str]]:
    parent = {identifier: identifier for identifier in ids}
    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key
    for a, b in pairs:
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    groups: dict[str, list[str]] = {}
    for key in sorted(ids):
        groups.setdefault(find(key), []).append(key)
    return sorted(groups.values())


def ssar_dependency_groups(units: list[dict], edges: list[dict], policy: Mapping,
                           *, admissible_refs: list[str] | None = None) -> dict:
    """Particiones conservadoras; las relaciones suministradas no se descubren."""
    validate_ssar_schema(policy, "Policy")
    registry = _index(units, "id")
    ids = sorted(registry)
    for unit in units:
        validate_ssar_schema(unit, "Unit")
        if unit["technique"] not in policy["technique_groups"]:
            raise ValueError("Técnica sin grupo SSAR.")
    equivalent = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if registry[a]["equivalence_key"] == registry[b]["equivalence_key"] or registry[a]["appearance_ref"] == registry[b]["appearance_ref"]:
                equivalent.append((a, b))
    dependence = list(equivalent)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if policy["technique_groups"][registry[a]["technique"]] == policy["technique_groups"][registry[b]["technique"]]:
                dependence.append((a, b))
    for edge in edges:
        validate_ssar_schema(edge, "Edge")
        _references([edge["a"], edge["b"]], registry, "grafo")
        if edge["a"] == edge["b"]:
            raise ValueError("Una dependencia requiere unidades distintas.")
        if edge["rule_id"] != policy["dependency_rules"][edge["relation"]]:
            raise ValueError("Regla de dependencia no declarada.")
        if edge["relation"] == "EQUIVALENT":
            if registry[edge["a"]]["equivalence_key"] != registry[edge["b"]]["equivalence_key"]:
                raise ValueError("Equivalencia con claves incompatibles.")
            equivalent.append((edge["a"], edge["b"]))
        if edge["relation"] != "SEMANTIC_OVERLAP":
            dependence.append((edge["a"], edge["b"]))
    admitted = set(ids if admissible_refs is None else admissible_refs)
    _references(list(admitted), registry, "unidades admitidas")
    effective = [[key for key in group if key in admitted] for group in _components(ids, dependence)]
    return {"units": deepcopy(sorted(units, key=lambda x: x["id"])), "edges": deepcopy(edges),
            "equivalence_classes": [{"id": "EQ:" + group[0], "unit_refs": group} for group in _components(ids, equivalent)],
            "effective_groups": [{"id": "GR:" + group[0], "unit_refs": group} for group in effective if group],
            "excluded_unit_refs": sorted(set(ids) - admitted),
            "grouping_rule_ref": "SSAR_CONSERVATIVE_CONNECTED_GROUPS_DEV_V1",
            "statistical_independence_established": False}


def _empty_result(enabled: bool) -> dict:
    return {"schema_version": CONTRACT_VERSION, "enabled": enabled,
            "policy_id": None, "policy_hash": None, "policy_status": "UNFROZEN",
            "analysis_scope": "EXPLORATORY", "execution_status": "not_run", "completion": "NONE",
            "coverage": [], "appearances": [], "qualified_significators": [], "secondary_support": [],
            "complexes": [], "mythic_dyads": [], "calculated_points": [], "hellenistic_lots": [],
            "temporal_activation": [], "documentary_correspondence": [], "dependency_graph": None,
            "external_validation_status": "NOT_PERFORMED", "structural_scoring_modified": False,
            "ontology_effect": "NONE", "discriminator_effect": "NONE"}


def run_ssar(request: Mapping[str, Any], *, policy: Mapping[str, Any] | None = None) -> dict:
    """Evalúa apariciones declaradas; no muta ni crea raíces o resultados core."""
    if type(request.get("enabled")) is not bool:
        raise ValueError("SSAR exige enabled booleano explícito.")
    result = _empty_result(request["enabled"])
    if not request["enabled"]:
        result["coverage"] = [{"layer": "SSAR", "status": "not_run", "completion": "NONE", "reason": "DISABLED", "assessed_refs": []}]
        return result
    policy = deepcopy(load_ssar_policy() if policy is None else policy)
    validate_ssar_request(request, policy)
    result.update(policy_id=policy["policy_id"], policy_hash=ssar_policy_hash(policy), policy_status="DEVELOPMENT")
    sources = _index(request.get("sources", []), "id")
    appearances = [_appearance(item, sources, policy) for item in request.get("appearances", [])]
    result["appearances"] = appearances
    result["qualified_significators"] = sorted(item["id"] for item in appearances if item["qualification"] == "QUALIFIED_SIGNIFICATOR")
    result["secondary_support"] = sorted(item["id"] for item in appearances if item["qualification"] == "SECONDARY_SUPPORT")
    units = request.get("units", [])
    if units:
        admitted = [unit["id"] for unit in units if unit["appearance_ref"] in set(result["qualified_significators"] + result["secondary_support"])]
        result["dependency_graph"] = ssar_dependency_groups(units, request.get("edges", []), policy, admissible_refs=admitted)
    executed = bool(appearances or units)
    result["execution_status"] = "executed" if executed else "not_run"
    result["completion"] = "PARTIAL" if executed else "NONE"
    result["coverage"] = [
        {"layer": "APPEARANCE_GATES", "status": "executed" if appearances else "not_run", "completion": "COMPLETE" if appearances else "NONE", "reason": "SUPPLIED_APPEARANCES_ONLY" if appearances else "NO_APPEARANCES_SUPPLIED", "assessed_refs": [item["id"] for item in appearances]},
        {"layer": "DEPENDENCY_GROUPING", "status": "executed" if units else "not_run", "completion": "COMPLETE" if units else "NONE", "reason": "DECLARED_DEPENDENCIES_ONLY" if units else "NO_UNITS_SUPPLIED", "assessed_refs": [item["id"] for item in units]},
    ] + [{"layer": layer, "status": "blocked", "completion": "NONE", "reason": "NOT_IMPLEMENTED_IN_PHASE2", "assessed_refs": []} for layer in policy["unimplemented_layers"]]
    _validate_ssar_result_structure(result, policy=policy)
    return result


def _validate_ssar_result_structure(result: Mapping[str, Any], *, policy: Mapping[str, Any] | None = None) -> None:
    validate_ssar_schema(result, "Result")
    appearances = _index(result["appearances"], "id")
    for field, qualification in (("qualified_significators", "QUALIFIED_SIGNIFICATOR"), ("secondary_support", "SECONDARY_SUPPORT")):
        expected = {key for key, value in appearances.items() if value["qualification"] == qualification}
        if set(result[field]) != expected:
            raise ValueError("Las referencias SSAR no coinciden con su cualificación.")
    for item in appearances.values():
        expected = {"QUALIFIED_SIGNIFICATOR": "SUPPORTED", "SECONDARY_SUPPORT": "COMPATIBLE", "BLOCKED": "NOT_EVALUABLE", "NO_CONTACT": "CONTRADICTED"}[item["qualification"]]
        if item["assessment"]["status"] != expected:
            raise ValueError("Estado incompatible con la cualificación de aparición.")
        if item["assessment"]["policy_ref"] != result["policy_id"]:
            raise ValueError("La evaluación SSAR no referencia su política efectiva.")
        if item["qualification"] == "QUALIFIED_SIGNIFICATOR" and (not item["core_root_refs"] or not item["source_refs"] or item["gate_reasons"] or item["matched_aspect"] is None or item["robustness"] is None):
            raise ValueError("La aparición cualificada tiene gates incompletos.")
        robust = item["robustness"]
        if robust is not None:
            if robust["preserved_count"] > robust["sample_count"] or robust["preserved_fraction"] != robust["preserved_count"] / robust["sample_count"]:
                raise ValueError("Resumen de robustez SSAR aritméticamente incoherente.")
        matched = item["matched_aspect"]
        if matched is not None:
            if matched["orb"] > matched["orb_limit"] or matched["orb"] != abs(matched["distance"] - matched["angle"]):
                raise ValueError("Resumen de geometría SSAR incoherente.")
            if matched["exactness"] != max(0.0, 1.0 - (matched["orb"] / matched["orb_limit"]) ** 2):
                raise ValueError("Exactitud geométrica SSAR incoherente.")
    coverage = _index(result["coverage"], "layer")
    for layer in coverage.values():
        if layer["status"] == "executed":
            if layer["completion"] == "NONE":
                raise ValueError("Cobertura ejecutada sin completitud declarada.")
        elif layer["completion"] != "NONE" or layer["assessed_refs"]:
            raise ValueError("Una capa no ejecutada no puede contener resultados.")
        if layer["status"] == "not_applicable" and not layer["reason"]:
            raise ValueError("not_applicable requiere motivo.")
    if result["enabled"]:
        if not {"APPEARANCE_GATES", "DEPENDENCY_GROUPING"} <= set(coverage):
            raise ValueError("Falta cobertura de las capacidades de fase 2.")
        if set(coverage["APPEARANCE_GATES"]["assessed_refs"]) != set(appearances):
            raise ValueError("La cobertura de apariciones no referencia sus resultados.")
    executed = [layer for layer in coverage.values() if layer["status"] == "executed"]
    if bool(executed) != (result["execution_status"] == "executed"):
        raise ValueError("Resumen SSAR incompatible con la cobertura.")
    if result["completion"] == "COMPLETE" and any(layer["status"] in {"blocked", "not_run"} or layer["completion"] == "PARTIAL" for layer in coverage.values()):
        raise ValueError("Una salida incompleta no puede declarar COMPLETE.")
    if policy is not None and result["enabled"]:
        if result["policy_id"] != policy["policy_id"] or result["policy_hash"] != ssar_policy_hash(policy):
            raise ValueError("Identidad o hash de política SSAR incoherente.")
        if not set(policy["unimplemented_layers"]) <= set(coverage):
            raise ValueError("Falta cobertura de capas SSAR pendientes.")
        for name in policy["unimplemented_layers"]:
            if coverage[name]["status"] != "blocked":
                raise ValueError("Una capacidad pendiente no puede declararse ejecutada ni no aplicable.")
        for item in appearances.values():
            point = policy["point_rules"].get(item["point_id"])
            if item["function_id"] != (point["function_id"] if point else None) or item["assessment"]["rule_ref"] != (point["rule_id"] if point else None):
                raise ValueError("La función o regla no corresponden al catálogo de la política.")
            if point and point["kind"] != item["kind"]:
                raise ValueError("Tipo de aparición incompatible con su política.")
            rule = policy["type_rules"][item["kind"]]
            matched = item["matched_aspect"]
            if matched is not None:
                spec = (rule["aspect_policy"] or {}).get(matched["aspect"])
                if spec is None or matched["angle"] != spec["angle"] or matched["orb_limit"] != spec["orb"]:
                    raise ValueError("La geometría no corresponde al orbe y aspecto declarados.")
            robust = item["robustness"]
            if robust is not None and (robust["rule_ref"] != rule["robustness_rule_id"] or robust["required_fraction"] != rule["minimum_preserved_fraction"] or robust["sample_count"] < rule["minimum_samples"]):
                raise ValueError("La robustez no corresponde a la regla publicada.")
            if item["qualification"] == "QUALIFIED_SIGNIFICATOR":
                if point is None or (item["project_method"] and not point["allow_project_method"]) or robust["preserved_fraction"] < rule["minimum_preserved_fraction"]:
                    raise ValueError("Cualificación SSAR incompatible con la política.")
    graph = result["dependency_graph"]
    if graph is not None:
        units = _index(graph["units"], "id")
        if set(coverage["DEPENDENCY_GROUPING"]["assessed_refs"]) != set(units):
            raise ValueError("La cobertura de dependencias no corresponde a sus unidades.")
        _index(graph["equivalence_classes"], "id")
        _index(graph["effective_groups"], "id")
        for unit in units.values():
            _references([unit["appearance_ref"]], appearances, "grafo/aparición")
        for family in ("equivalence_classes", "effective_groups"):
            members = [key for group in graph[family] for key in group["unit_refs"]]
            _references(members, units, family)
            if len(members) != len(set(members)) or any(not group["unit_refs"] for group in graph[family]):
                raise ValueError("Las particiones SSAR contienen doble pertenencia o grupos vacíos.")
        equivalents = {key for group in graph["equivalence_classes"] for key in group["unit_refs"]}
        effective = {key for group in graph["effective_groups"] for key in group["unit_refs"]}
        excluded = set(graph["excluded_unit_refs"])
        if equivalents != set(units) or effective & excluded or effective | excluded != set(units):
            raise ValueError("La partición no cubre exactamente las unidades.")
        admitted = {key for key, unit in units.items() if unit["appearance_ref"] in set(result["qualified_significators"] + result["secondary_support"])}
        if effective != admitted:
            raise ValueError("Unidades bloqueadas contadas como apoyo efectivo.")
        if policy is not None:
            expected_graph = ssar_dependency_groups(list(units.values()), graph["edges"], policy, admissible_refs=sorted(admitted))
            if graph != expected_graph:
                raise ValueError("La agrupación SSAR no reproduce su política.")
    elif result["enabled"] and coverage["DEPENDENCY_GROUPING"]["assessed_refs"]:
        raise ValueError("Cobertura de unidades sin grafo de dependencia.")


def validate_ssar_result(result: Mapping[str, Any], *, policy: Mapping[str, Any] | None = None,
                         request: Mapping[str, Any] | None = None) -> None:
    """Valida estructura y política; resultados efectivos exigen entrada para reproducirse."""
    _validate_ssar_result_structure(result, policy=policy)
    if (result["appearances"] or result["dependency_graph"] is not None) and (request is None or policy is None):
        raise ValueError("La validación de referencias efectivas requiere entrada y política.")
    if request is not None:
        if policy is None:
            raise ValueError("La reproducción de salida necesita política.")
        if result != run_ssar(request, policy=policy):
            raise ValueError("La salida SSAR no reproduce la entrada declarada.")
