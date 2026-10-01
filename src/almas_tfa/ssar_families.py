"""Familias y díadas SSAR optativas, sobre apariciones y raíces upstream."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect
from .ssar import _finite_tree, _index, assess_ssar_claim, run_ssar, validate_ssar_schema

VERSION = "ssar-families-1.0-development"


def _load(name: str) -> dict:
    return json.loads(resources.files("almas_tfa").joinpath("data", name).read_text(encoding="utf-8"))


def load_families_catalog() -> dict:
    return _load("ssar-families-catalog.json")


def load_families_policy() -> dict:
    policy = _load("ssar-families-development-policy.json")
    validate_ssar_schema(policy, "Policy")
    return policy


def families_catalog_hash() -> str:
    value = json.dumps(load_families_catalog(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return sha256(value.encode("utf-8")).hexdigest()


def validate_families_schema(value: Mapping, definition: str) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError("Familias SSAR requiere el extra schema-validation.") from exc
    schema = _load("ssar-contract-definitions.json")
    if definition not in schema["$defs"]:
        raise ValueError("Definición de familias SSAR desconocida.")
    schema["$ref"] = "#/$defs/" + definition
    _finite_tree(value)
    Draft202012Validator(schema).validate(value)


def build_families_request(request: Mapping) -> dict:
    """Construye apariciones sin inventar posiciones o raíces; unidades por observación."""
    validate_families_schema(request, "F4Request")
    if not request["enabled"]:
        return {"enabled": False}
    catalog = load_families_catalog()
    entries = _index(catalog["entries"], "point_id")
    _index(request.get("observations", []), "id")
    appearances, units, seen = [], [], set()
    for observation in request.get("observations", []):
        point = observation["point_id"]
        geometry = observation["geometry"]
        technique, subject = observation["technique"], observation["subject_id"]
        if (technique == "SYNASTRY") != (subject in {"A", "B"}):
            raise ValueError("Sinastría exige sujeto A/B; compuesto/Davison, RELATIONSHIP.")
        if geometry:
            # Una misma geometría puede pertenecer a cartas distintas, nunca duplicarse dentro de la misma.
            signature = (point, subject, technique, geometry["frame"], geometry["target_id"],
                         geometry["longitude"] % 360, geometry["target_longitude"] % 360,
                         tuple(sorted(observation["core_root_refs"])))
            if signature in seen:
                raise ValueError("El contacto debe usar una aparición compartida.")
            seen.add(signature)
        appearance = {key: deepcopy(observation[key]) for key in
                      ("id", "point_id", "geometry", "core_root_refs", "core_anchor_search_complete", "robustness")}
        appearance.update(kind="NAMED_SMALL_BODY")
        appearance.update({key: deepcopy(entries[point][key]) for key in ("provenance", "semantic_basis", "method")})
        appearances.append(appearance)
        units.append({"id": "U:" + observation["id"], "appearance_ref": observation["id"],
                      "technique": technique, "equivalence_key": observation["evidence_key"]})
    return {"enabled": True, "sources": deepcopy(catalog["sources"]),
            "core_roots": deepcopy(request.get("core_roots", [])), "appearances": appearances,
            "units": units, "edges": deepcopy(request.get("edges", []))}


def _cross_contacts(request: Mapping, catalog: Mapping) -> list[dict]:
    observations = _index(request.get("observations", []), "id")
    entries = _index(catalog["entries"], "point_id")
    _index(request.get("cross_contacts", []), "id")
    rule = catalog["complex_rule"]
    output, seen = [], set()
    for contact in request.get("cross_contacts", []):
        if contact["subject_a"] == contact["subject_b"]:
            raise ValueError("El contacto cruzado exige dos sujetos distintos.")
        for point in (contact["point_a"], contact["point_b"]):
            if point not in entries:
                raise ValueError("Cuerpo cruzado sin identidad en el catálogo.")
        geometry, robust = contact["geometry"], contact["robustness"]
        direction = "A_TO_B" if contact["subject_a"] == "A" else "B_TO_A"
        item = {"id": contact["id"], "direction": direction, "status": "BLOCKED",
                "matched_aspect": None, "robustness": None,
                "endpoint_appearance_refs": sorted(contact["endpoint_appearance_refs"]),
                "reason": "GEOMETRY_OR_PRECISION_MISSING"}
        if geometry:
            if geometry["target_id"] != contact["point_b"]:
                raise ValueError("El target cruzado debe coincidir con el segundo cuerpo.")
            signature = (contact["point_a"], contact["subject_a"], contact["point_b"],
                         contact["subject_b"], geometry["frame"],
                         geometry["longitude"] % 360, geometry["target_longitude"] % 360)
            reverse = (contact["point_b"], contact["subject_b"], contact["point_a"],
                       contact["subject_a"], geometry["frame"],
                       geometry["target_longitude"] % 360, geometry["longitude"] % 360)
            if signature in seen or reverse in seen:
                raise ValueError("El mismo contacto cruzado requiere una referencia compartida.")
            seen.add(signature)
        if robust:
            _index(robust["samples"], "id")
            offsets = [s["offset_minutes"] for s in robust["samples"]]
            if len(offsets) != len(set(offsets)):
                raise ValueError("Offsets cruzados duplicados.")
        for ref in contact["endpoint_appearance_refs"]:
            if ref not in observations:
                raise ValueError("Anclaje cruzado sin aparición existente.")
            obs = observations[ref]
            if obs["technique"] != "SYNASTRY":
                raise ValueError("Un endpoint cruzado exige sinastría.")
            endpoint = next((side for side in ("a", "b") if obs["point_id"] == contact["point_" + side]
                             and obs["subject_id"] == contact["subject_" + side]), None)
            if endpoint is None:
                raise ValueError("Identidad o sujeto del anclaje cruzado incompatible.")
            field = "longitude" if endpoint == "a" else "target_longitude"
            if geometry is None or obs["geometry"] is None or geometry[field] % 360 != obs["geometry"]["longitude"] % 360:
                raise ValueError("La posición del endpoint no reproduce la aparición anclada.")
            if robust and obs["robustness"]:
                expected = {s["offset_minutes"]: s[field] % 360 for s in robust["samples"]}
                actual = {s["offset_minutes"]: s["longitude"] % 360 for s in obs["robustness"]["samples"]}
                if expected != actual:
                    raise ValueError("Las perturbaciones del endpoint no reproducen el anclaje.")
        if any(entries[point]["provenance"]["identity_status"] != "VERIFIED"
               for point in (contact["point_a"], contact["point_b"])):
            item["reason"] = "BODY_IDENTITY_UNRESOLVED"
        elif geometry and robust and robust["input_precision_sufficient"] is True and set(
            s["offset_minutes"] for s in robust["samples"]) == set(rule["sample_offsets_minutes"]):
            match = match_declared_aspect(geometry["longitude"], geometry["target_longitude"], rule["aspect_policy"])
            item["matched_aspect"] = match
            if match is None:
                item.update(status="NO_CONTACT", reason="NO_DECLARED_CROSS_CONTACT")
            else:
                matches = [match_declared_aspect(s["longitude"], s["target_longitude"], rule["aspect_policy"])
                           for s in robust["samples"]]
                preserved = sum(m is not None and m["aspect"] == match["aspect"] for m in matches)
                fraction = preserved / len(matches)
                item["robustness"] = {"rule_ref": rule["rule_id"], "sample_count": len(matches),
                                     "preserved_count": preserved, "preserved_fraction": fraction,
                                     "required_fraction": rule["minimum_preserved_fraction"]}
                item.update(status="CONTACT" if fraction >= rule["minimum_preserved_fraction"] else "BLOCKED",
                            reason="ROBUST_CROSS_CONTACT" if fraction >= rule["minimum_preserved_fraction"] else "CROSS_ROBUSTNESS_INSUFFICIENT")
        output.append(item)
    return sorted(output, key=lambda item: item["id"])


def _group_refs(refs: list[str], ssar: Mapping) -> list[str]:
    graph = ssar["dependency_graph"]
    if graph is None:
        return []
    unit_ids = {u["id"] for u in graph["units"] if u["appearance_ref"] in refs}
    return sorted(g["id"] for g in graph["effective_groups"] if unit_ids.intersection(g["unit_refs"]))


def _family(spec: Mapping, appearances: Mapping, ssar: Mapping, *, overlay: bool = False) -> dict:
    components, admitted = [], []
    for point in spec["members"]:
        refs = sorted(key for key, a in appearances.items() if a["point_id"] == point)
        good = sorted(key for key in refs if appearances[key]["qualification"] in {"QUALIFIED_SIGNIFICATOR", "SECONDARY_SUPPORT"})
        admitted.extend(good)
        components.append({"point_id": point, "appearance_refs": refs, "admissible_refs": good,
                           "coverage": "MISSING" if not refs else "BLOCKED" if not good else "SUPPLIED"})
    return {"id": spec["id"], "components": components, "contact_refs": sorted(admitted),
            "effective_group_refs": [] if overlay else _group_refs(admitted, ssar),
            "cluster_strength": None, "selection_policy": "NO_RANKING_WITHOUT_FROZEN_COMMON_MAGNITUDE",
            "coverage": "SUPPLIED" if all(c["coverage"] == "SUPPLIED" for c in components) else "PARTIAL",
            "independent_function": not overlay}


def _assessment(scope: str, policy: Mapping, rule: Mapping, **kwargs) -> dict:
    return assess_ssar_claim(scope=scope, policy_ref=policy["policy_id"], rule_ref=rule["rule_id"], **kwargs)


def _dyad(selection: Mapping, spec: Mapping, observations: Mapping, appearances: Mapping,
          contacts: Mapping, cross_results: Mapping, ssar: Mapping, policy: Mapping, rule: Mapping) -> dict:
    refs, cross_refs = selection["appearance_refs"], selection["cross_contact_refs"]
    if set(refs) - set(appearances) or set(cross_refs) - set(contacts):
        raise ValueError("Referencias de díada rotas.")
    if any(appearances[ref]["point_id"] not in spec["members"] for ref in refs):
        raise ValueError("Aparición ajena a los componentes de la díada.")
    directions = set()
    for ref in cross_refs:
        c = contacts[ref]
        if [c["point_a"], c["point_b"]] != spec["members"]:
            raise ValueError("El orden de los cuerpos cruzados debe coincidir con la díada.")
        if not set(c["endpoint_appearance_refs"]) <= set(refs):
            raise ValueError("El anclaje cruzado no pertenece a las apariciones seleccionadas.")
        directions.add(cross_results[ref]["direction"])
    admitted = sorted(ref for ref in refs if appearances[ref]["qualification"] in {"QUALIFIED_SIGNIFICATOR", "SECONDARY_SUPPORT"})
    # Afrodita es overlay y nunca alcanza este conjunto: no forma parte de ninguna díada.
    core_refs = sorted({root for ref in admitted for root in appearances[ref]["core_root_refs"]})
    groups = _group_refs(admitted, ssar)
    qualified = any(appearances[ref]["qualification"] == "QUALIFIED_SIGNIFICATOR" for ref in admitted)
    components = set(appearances[ref]["point_id"] for ref in admitted) == set(spec["members"])
    covered = selection["search_complete"] and directions == {"A_TO_B", "B_TO_A"} and all(
        cross_results[ref]["status"] != "BLOCKED" for ref in cross_refs)
    positive_directions, geometric_directions, negative = set(), set(), []
    for ref in cross_refs:
        result, c = cross_results[ref], contacts[ref]
        # Un contacto secundario-secundario no produce su propio anclaje core.
        anchored = any(endpoint in admitted and appearances[endpoint]["core_root_refs"]
                       and appearances[endpoint]["robustness"]
                       and appearances[endpoint]["robustness"]["preserved_fraction"] >= rule["minimum_preserved_fraction"]
                       for endpoint in c["endpoint_appearance_refs"])
        if result["status"] == "CONTACT":
            geometric_directions.add(result["direction"])
            if anchored:
                positive_directions.add(result["direction"])
    for direction in directions - positive_directions:
        candidates = [ref for ref in cross_refs if cross_results[ref]["direction"] == direction]
        if candidates and all(cross_results[ref]["status"] == "NO_CONTACT" for ref in candidates):
            negative.extend(candidates)
    both_contacts = positive_directions == {"A_TO_B", "B_TO_A"}
    blockers = list(spec["blockers"])
    if not covered:
        blockers.append("CROSS_DIRECTIONAL_COVERAGE_INCOMPLETE")
    if not both_contacts:
        blockers.append("BIDIRECTIONAL_ANCHORED_CONTACTS_NOT_MET")
    if not components:
        blockers.append("COMPONENT_QUALIFICATION_INCOMPLETE")
    if not qualified:
        blockers.append("QUALIFIED_SIGNIFICATOR_MISSING")
    if len(groups) < rule["minimum_effective_groups"]:
        blockers.append("TWO_EFFECTIVE_GROUPS_NOT_MET")
    if not core_refs:
        blockers.append("CORE_ANCHOR_MISSING")
    structural = _assessment("STRUCTURAL_GEOMETRY", policy, rule, coverage_sufficient=covered,
                             positive_complete=geometric_directions == {"A_TO_B", "B_TO_A"}, compatible=bool(geometric_directions),
                             evidence_refs=cross_refs, excluding_counterevidence_refs=negative,
                             counterevidence_evaluable=bool(negative) and selection["search_complete"])
    functional_coverage = covered and not spec["blockers"] and all(
        appearances[ref]["qualification"] != "BLOCKED" for ref in refs) and bool(refs)
    complete = functional_coverage and both_contacts and components and qualified and bool(core_refs) and len(groups) >= rule["minimum_effective_groups"]
    functional = _assessment("FUNCTIONAL_INTERPRETATION", policy, rule,
                             coverage_sufficient=functional_coverage, positive_complete=complete,
                             compatible=bool(admitted) and bool(positive_directions) and components,
                             evidence_refs=admitted + cross_refs)
    return {"id": spec["id"], "members": list(spec["members"]), "appearance_refs": sorted(refs),
            "cross_contact_refs": sorted(cross_refs), "admissible_refs": admitted,
            "effective_group_refs": groups, "core_root_refs": core_refs,
            "qualified_complex": complete, "assessments": {
                "structural_geometry": structural, "functional_interpretation": functional,
                "temporal_activation": _assessment("TEMPORAL_ACTIVATION", policy, rule, coverage_sufficient=False),
                "documentary_correspondence": _assessment("DOCUMENTARY_STRUCTURAL_CORRESPONDENCE", policy, rule, coverage_sufficient=False)},
            "blockers": sorted(set(blockers)), "source_refs": sorted(spec["source_refs"]),
            "epistemic_class": "E_PROJECT_HYPOTHESIS", "documentary_scope": "STRUCTURAL",
            "cluster_strength": None,
            "inferential_limit": "Hipótesis funcional E: no demuestra Mónada, reciprocidad, retorno vivido, reunión ni origen común."}


def run_families(request: Mapping[str, Any]) -> dict:
    """Sin score, estado global, efemérides, eventos, M27 ni efectos en el núcleo."""
    if type(request.get("enabled")) is not bool:
        raise ValueError("Familias SSAR exige enabled explícito.")
    output = {"schema_version": VERSION, "enabled": request["enabled"], "catalog_id": None,
              "catalog_hash": None, "policy_id": None, "policy_status": "DEVELOPMENT",
              "ssar": run_ssar({"enabled": False}), "families": [], "overlays": [],
              "cross_contacts": [], "dyads": [], "shared_contacts": [], "completion": "NONE",
              "external_validation_status": "NOT_PERFORMED", "structural_scoring_modified": False,
              "ontology_effect": "NONE", "discriminator_effect": "NONE"}
    if not request["enabled"]:
        return output
    effective = build_families_request(request)
    catalog, policy = load_families_catalog(), load_families_policy()
    ssar = run_ssar(effective, policy=policy)
    appearances = _index(ssar["appearances"], "id")
    observations = _index(request.get("observations", []), "id")
    contacts = _index(request.get("cross_contacts", []), "id")
    cross = _cross_contacts(request, catalog)
    cross_results = _index(cross, "id")
    specs = _index(catalog["dyads"], "id")
    _index(request.get("dyads", []), "id")
    dyads = [_dyad(s, specs[s["id"]], observations, appearances, contacts, cross_results,
                   ssar, policy, catalog["complex_rule"]) for s in request.get("dyads", [])]
    families = [_family(spec, appearances, ssar) for spec in catalog["families"]]
    overlays = [_family(spec, appearances, ssar, overlay=True) for spec in catalog["overlays"]]
    consumers: dict[str, list[str]] = {}
    for item in families + overlays + dyads:
        for ref in item.get("appearance_refs", item.get("contact_refs", [])):
            consumers.setdefault(ref, []).append(item["id"])
    output.update(catalog_id=catalog["catalog_id"], catalog_hash=families_catalog_hash(),
                  policy_id=policy["policy_id"], ssar=ssar, families=families, overlays=overlays,
                  cross_contacts=cross, dyads=sorted(dyads, key=lambda d: d["id"]),
                  shared_contacts=[{"appearance_ref": ref, "consumer_refs": sorted(set(ids)),
                                    "contributes_new_evidence": False}
                                   for ref, ids in sorted(consumers.items()) if len(set(ids)) > 1],
                  completion="PARTIAL" if observations or cross or dyads else "NONE")
    validate_families_schema(output, "F4Result")
    return output


def validate_families_result(result: Mapping, *, request: Mapping) -> None:
    """Reproduce identidades, fuentes, contactos, particiones y cuatro alcances."""
    validate_families_schema(result, "F4Result")
    if result != run_families(request):
        raise ValueError("La salida de familias no reproduce la entrada y política.")
