"""Retirada vestal: política exploratoria, descriptiva y sin efecto ontológico.

Consume hechos fechados y geometrías verificadas aguas arriba. No calcula
efemérides, diagnostica estados clínicos ni infiere la conducta de otra persona.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from importlib import resources
import json
import math
from typing import Any, Mapping

from .corpus_doctrine import corpus_source_trace

POLICY_ID = "ALMAS_SURRENDER_VESTAL_V1"
STATES = {"ABSENT", "EMERGING", "ACTIVE", "INTEGRATED", "NOT_EVALUABLE"}
STATUSES = {"SUPPORTED", "COMPATIBLE", "INSUFFICIENT", "CONTRADICTED", "NOT_EVALUABLE"}


def load_surrender_vestal_policy() -> dict[str, Any]:
    with resources.files("almas_tfa").joinpath("data", "surrender-vestal-policy.json").open(encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy["policy_id"] != POLICY_ID:
        raise ValueError("Política de retirada vestal desconocida.")
    return policy


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} requiere texto no vacío.")
    return value


def _date(value: Any, label: str) -> date:
    try:
        parsed = date.fromisoformat(_text(value, label))
        if parsed.isoformat() != value:
            raise ValueError("Formato de fecha no canónico.")
        return parsed
    except ValueError as exc:
        raise ValueError(f"{label} requiere fecha ISO completa.") from exc


def _refs(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} requiere referencias explícitas.")
    return sorted({_text(item, label) for item in value})


def _items(value: Any, label: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, Mapping) for item in value):
        raise ValueError(f"{label} debe ser una lista de objetos.")
    return value


def _assessment(state: str, status: str, refs: list[str]) -> dict[str, Any]:
    return {"state": state, "status": status, "evidence_refs": sorted(set(refs))}


def _components(signals: list[dict[str, Any]]) -> list[list[str]]:
    """Cierre transitivo por raíz o dependencias declaradas; nunca por etiqueta temática."""
    groups: list[tuple[set[str], set[str]]] = []
    for signal in signals:
        keys = {"ROOT:" + signal["root_id"]} | {"DEP:" + key for key in signal["dependency_keys"]}
        members = {signal["signal_id"]}
        remaining = []
        for old_keys, old_members in groups:
            if keys & old_keys:
                keys |= old_keys
                members |= old_members
            else:
                remaining.append((old_keys, old_members))
        # La ampliación puede enlazar un componente recorrido anteriormente.
        while any(keys & old_keys for old_keys, _ in remaining):
            next_remaining = []
            for old_keys, old_members in remaining:
                if keys & old_keys:
                    keys |= old_keys
                    members |= old_members
                else:
                    next_remaining.append((old_keys, old_members))
            remaining = next_remaining
        groups = remaining + [(keys, members)]
    return sorted((sorted(members) for _, members in groups), key=lambda group: group[0])


def assess_surrender_vestal(request: Mapping[str, Any]) -> dict[str, Any]:
    """Clasifica un único sujeto en una ventana declarada; no produce puntuaciones."""
    if not isinstance(request, Mapping):
        raise ValueError("surrender_vestal requiere un objeto.")
    policy = load_surrender_vestal_policy()
    doctrine_trace = corpus_source_trace(request.get("doctrinal_source_refs", []))
    subject = _text(request.get("subject_id"), "subject_id")
    start = _date(request.get("window_start"), "window_start")
    end = _date(request.get("window_end"), "window_end")
    if start > end:
        raise ValueError("La ventana no puede estar invertida.")
    accepted, rejected = [], []
    seen: set[str] = set()
    codes = set(policy["observation_codes"])
    for raw in _items(request.get("observations", []), "observations"):
        ident = _text(raw.get("observation_id"), "observation_id")
        if ident in seen:
            raise ValueError(f"Observación duplicada: {ident}")
        seen.add(ident)
        _text(raw.get("subject_id"), "observation.subject_id")
        if raw.get("code") not in codes or not isinstance(raw.get("value"), bool):
            raise ValueError(f"{ident}: código o valor de observación inválido.")
        dated = _date(raw.get("date"), ident + ".date")
        refs = _refs(raw.get("source_refs"), ident + ".source_refs")
        reasons = []
        if raw["subject_id"] != subject:
            reasons.append("OTHER_SUBJECT")
        if not start <= dated <= end:
            reasons.append("OUTSIDE_WINDOW")
        if raw.get("documentary_quality") not in policy["accepted_documentary_qualities"]:
            reasons.append("INSUFFICIENT_DOCUMENTARY_QUALITY")
        if raw.get("fact_interpretation_separated") is not True:
            reasons.append("FACT_INTERPRETATION_NOT_SEPARATED")
        if raw.get("record_status", "ACTIVE") != "ACTIVE":
            reasons.append("SUPERSEDED_OR_INACTIVE")
        if reasons:
            rejected.append({"id": ident, "reasons": reasons})
        else:
            accepted.append({
                "observation_id": ident, "subject_id": subject, "code": raw["code"],
                "value": raw["value"], "date": raw["date"], "source_refs": refs,
                "documentary_quality": raw["documentary_quality"],
                "fact_interpretation_separated": True, "epistemic_class": "A_CALCULATED",
            })
    accepted.sort(key=lambda item: (item["date"], item["observation_id"]))
    positive = {item["code"] for item in accepted if item["value"]}
    ambiguous = {code for code in positive if any(item["code"] == code and not item["value"] for item in accepted)}
    usable = positive - ambiguous

    def refs_for(selected: set[str]) -> list[str]:
        return [item["observation_id"] for item in accepted if item["code"] in selected]

    surrender = {}
    for domain, spec in policy["domains"].items():
        supports = usable & set(spec["support"])
        conflicts = usable & set(spec["counter"])
        ids = refs_for(set(spec["support"]) | set(spec["counter"]))
        if ambiguous & (set(spec["support"]) | set(spec["counter"])) or (supports and conflicts):
            surrender[domain] = _assessment("EMERGING", "INSUFFICIENT", ids)
        elif conflicts:
            surrender[domain] = _assessment("ABSENT", "CONTRADICTED", ids)
        elif len(supports) >= policy["domain_active_distinct_codes"]:
            surrender[domain] = _assessment("ACTIVE", "SUPPORTED", ids)
        elif supports:
            surrender[domain] = _assessment("EMERGING", "COMPATIBLE", ids)
        else:
            surrender[domain] = _assessment("NOT_EVALUABLE", "NOT_EVALUABLE", ids)

    withdrawal_codes = set(policy["withdrawal_required_codes"])
    counter_codes = usable & (set(policy["strong_counterevidence_codes"]) | {"WITHDRAWAL_ABSENT"})
    counter = [{"code": code, "evidence_refs": refs_for({code}), "strength": "STRONG"} for code in sorted(counter_codes)]
    process_ambiguous = ambiguous - {"ABSTINENCE_DECLARED", "CELIBACY_CHOSEN"}
    counter += [{"code": "CONFLICTING_OBSERVATIONS", "evidence_refs": refs_for({code}), "strength": "UNRESOLVED"} for code in sorted(process_ambiguous)]
    has_withdrawal = withdrawal_codes <= usable
    if counter or "WITHDRAWAL_ABSENT" in usable:
        state = "EMERGING" if usable & withdrawal_codes else "ABSENT"
        status = "INSUFFICIENT" if usable & withdrawal_codes or process_ambiguous else "CONTRADICTED"
    elif has_withdrawal:
        state, status = "ACTIVE", "SUPPORTED"
        integrated = set(policy["integration_required_codes"]) <= usable
        dates = {item["date"] for item in accepted if item["value"] and item["code"] in set(policy["integration_required_codes"])}
        if integrated and len(dates) >= policy["integration_minimum_dates"] and all(item["status"] == "SUPPORTED" for item in surrender.values()):
            state = "INTEGRATED"
    elif usable & withdrawal_codes:
        state, status = "EMERGING", "COMPATIBLE"
    elif "WITHDRAWAL_ABSENT" in ambiguous:
        state, status = "NOT_EVALUABLE", "INSUFFICIENT"
    else:
        state, status = "NOT_EVALUABLE", "NOT_EVALUABLE"

    sexual = {}
    for output_key, code in (("abstinence", "ABSTINENCE_DECLARED"), ("celibacy", "CELIBACY_CHOSEN")):
        items = [item for item in accepted if item["code"] == code]
        values = {item["value"] for item in items}
        sexual[output_key] = {
            "value": next(iter(values)) if len(values) == 1 else None,
            "status": "SUPPORTED" if len(values) == 1 else ("INSUFFICIENT" if values else "NOT_EVALUABLE"),
            "evidence_refs": [item["observation_id"] for item in items],
            "scope": "DOCUMENTED_DECLARATION",
        }
    abstinent = sexual["abstinence"]["value"] is True or sexual["celibacy"]["value"] is True
    phenotypes = []
    if abstinent and "REACTIVE_ABSTINENCE" in usable:
        phenotypes.append("REACTIVE_ABSTINENCE")
    if abstinent and "WAITING_FOR_UNION" in usable:
        phenotypes.append("WAITING_CELIBACY")
    if state in {"ACTIVE", "INTEGRATED"}:
        phenotypes.append("VESTAL_WITHDRAWAL")
    if surrender["erotic"]["status"] == "SUPPORTED":
        phenotypes.append("EROTIC_INTEGRATION")

    roots = []
    root_ids = set()
    for raw in _items(request.get("structural_roots", []), "structural_roots"):
        ident = _text(raw.get("root_id"), "root_id")
        if ident in root_ids:
            raise ValueError(f"Raíz duplicada: {ident}")
        root_ids.add(ident)
        _text(raw.get("subject_id"), "root.subject_id")
        refs = _refs(raw.get("source_refs"), "root.source_refs")
        if raw["subject_id"] == subject and raw.get("verified") is True:
            roots.append({"root_id": ident, "subject_id": subject, "source_refs": refs, "verified": True})
    known_roots = {item["root_id"] for item in roots}
    signals, ignored = [], []
    signal_ids = set()
    for raw in _items(request.get("temporal_activations", []), "temporal_activations"):
        ident = _text(raw.get("signal_id"), "signal_id")
        if ident in signal_ids:
            raise ValueError(f"Señal duplicada: {ident}")
        signal_ids.add(ident)
        for key in ("subject_id", "root_id", "technique", "symbolic_family"):
            _text(raw.get(key), ident + "." + key)
        if raw["technique"] not in policy["technique_groups"] or raw["symbolic_family"] not in policy["symbolic_families"]:
            raise ValueError(f"{ident}: técnica o familia simbólica no reconocida.")
        dated = _date(raw.get("date"), ident + ".date")
        source_refs = _refs(raw.get("source_refs"), ident + ".source_refs")
        dependencies = _refs(raw.get("dependency_keys"), ident + ".dependency_keys")
        orb, limit = raw.get("orb"), raw.get("declared_orb")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 for value in (orb, limit)):
            raise ValueError(f"{ident}: orbes finitos no negativos requeridos.")
        _text(raw.get("aspect_policy_ref"), ident + ".aspect_policy_ref")
        reasons = []
        if raw["subject_id"] != subject:
            reasons.append("OTHER_SUBJECT")
        if raw["root_id"] not in known_roots:
            reasons.append("UNVERIFIED_STRUCTURAL_ROOT")
        if not start <= dated <= end:
            reasons.append("OUTSIDE_WINDOW")
        if raw.get("verified") is not True or raw.get("temporal_correspondence_documented") is not True:
            reasons.append("UNVERIFIED_GEOMETRY_OR_TEMPORAL_CORRESPONDENCE")
        if orb > limit:
            reasons.append("OUTSIDE_DECLARED_ORB")
        if reasons:
            ignored.append({"id": ident, "reasons": reasons})
        else:
            signals.append({
                "signal_id": ident, "subject_id": subject, "root_id": raw["root_id"],
                "technique": raw["technique"], "technique_group": policy["technique_groups"][raw["technique"]],
                "symbolic_family": raw["symbolic_family"], "date": raw["date"],
                "source_refs": source_refs, "dependency_keys": dependencies,
                "orb": orb, "declared_orb": limit, "aspect_policy_ref": raw["aspect_policy_ref"],
                "epistemic_class": "B_TECHNIQUE",
            })
    signals.sort(key=lambda item: item["signal_id"])
    components = _components(signals)
    groups = {item["technique_group"] for item in signals}
    families = {item["symbolic_family"] for item in signals}
    # Exigir Vesta y otra familia en componentes distintos, sin promover dracónica.
    component_by_id = {ident: index for index, members in enumerate(components) for ident in members}
    independent_pair = any(
        left["symbolic_family"] == "VESTA" and right["symbolic_family"] != "VESTA"
        and left["technique_group"] != "CORROBORATIVE" and right["technique_group"] != "CORROBORATIVE"
        and left["technique_group"] != right["technique_group"]
        and component_by_id[left["signal_id"]] != component_by_id[right["signal_id"]]
        for left in signals for right in signals
    )
    if counter:
        astro_status = "INSUFFICIENT" if signals else "NOT_EVALUABLE"
    elif independent_pair and has_withdrawal:
        astro_status = "SUPPORTED"
    elif signals:
        astro_status = "COMPATIBLE"
    else:
        astro_status = "NOT_EVALUABLE"
    return {
        "policy_id": POLICY_ID, "subject_id": subject,
        "window_start": start.isoformat(), "window_end": end.isoformat(),
        "surrender": surrender,
        "vestal_withdrawal": _assessment(state, status, refs_for(withdrawal_codes | set(policy["integration_required_codes"]) | {"WITHDRAWAL_ABSENT"})),
        "sexual_observations": sexual, "phenotypes": sorted(phenotypes),
        "documented_behaviors": accepted, "rejected_observations": rejected,
        "counterevidence": counter, "structural_roots": sorted(roots, key=lambda item: item["root_id"]),
        "temporal_activations": signals, "rejected_activations": ignored,
        "dependencies": components,
        "astrological_correspondence": {
            "status": astro_status, "independent_component_count": len(components),
            "technique_groups": sorted(groups), "symbolic_families": sorted(families),
            "scope": "PERSONAL_SYMBOLIC_PHASE_ACTIVATION",
        },
        "relational_activation": {"status": "NOT_EVALUABLE", "reason": "La evaluación personal no establece activación bilateral."},
        "outcome": {"status": "NOT_EVALUABLE", "value": None},
        "ontology_effect": "NONE", "structural_scoring_modified": False,
        "iat_modified": False, "score_created": False,
        "traceability": {
            "documentary_behavior": {"observation_refs": [item["observation_id"] for item in accepted], "scope": "DOCUMENTED_BEHAVIOR"},
            "doctrinal_correspondence": dict(doctrine_trace, scope="COMPARATIVE_CONTEXT_ONLY"),
            "symbolic_astrological_activation": {"signal_refs": [item["signal_id"] for item in signals], "scope": "PERSONAL_SYMBOLIC_PHASE_ACTIVATION"},
        },
        "epistemic_class": "E_PROJECT_HYPOTHESIS", "policy_status": "EXPLORATORY",
        "limitations": [
            "Los estados describen ajuste a una política experimental; no certifican una ontología ni validación empírica externa.",
            "La abstinencia y el celibato sólo se registran por declaración documentada; no se infieren desde geometrías.",
            "La integración no implica reunión ni permite inferir sexualidad, fidelidad, sentimientos o decisiones ajenos.",
        ],
    }


def validate_surrender_vestal_result(result: Mapping[str, Any]) -> None:
    """Reproducir el resultado desde su evidencia minimizada; bloquear manipulación."""
    if not isinstance(result, Mapping) or result.get("policy_id") != POLICY_ID:
        raise ValueError("Resultado de retirada vestal inválido.")
    signals = [dict(item, verified=True, temporal_correspondence_documented=True) for item in result.get("temporal_activations", [])]
    request = {key: result.get(key) for key in ("subject_id", "window_start", "window_end", "structural_roots")}
    request.update(observations=result.get("documented_behaviors", []), temporal_activations=signals)
    request["doctrinal_source_refs"] = result.get("traceability", {}).get("doctrinal_correspondence", {}).get("source_refs", [])
    reproduced = assess_surrender_vestal(request)
    if set(result) != set(reproduced):
        raise ValueError("El resultado contiene campos ausentes o no declarados.")
    for field in ("rejected_observations", "rejected_activations"):
        for item in _items(result[field], field):
            if set(item) != {"id", "reasons"}:
                raise ValueError("Registro de rechazo inválido.")
            _text(item["id"], field + ".id")
            _refs(item["reasons"], field + ".reasons")
    for key in reproduced:
        if key in {"rejected_observations", "rejected_activations"}:
            continue
        if json.dumps(result.get(key), sort_keys=True, allow_nan=False) != json.dumps(reproduced[key], sort_keys=True, allow_nan=False):
            raise ValueError(f"Resultado de retirada vestal no reproducible: {key}")


def surrender_vestal_report_paragraphs(result: Mapping[str, Any]) -> list[str]:
    """Texto español reutilizable por autoría personal y relacional."""
    validate_surrender_vestal_result(result)
    withdrawal = result["vestal_withdrawal"]
    sexual = result["sexual_observations"]
    def label(item: Mapping[str, Any]) -> str:
        return "no evaluable" if item["value"] is None else ("declarada" if item["value"] else "declarada ausente")
    return [
        f"Para el sujeto {result['subject_id']}, entre {result['window_start']} y {result['window_end']}, la retirada vestal se clasifica {withdrawal['state']} con respaldo {withdrawal['status']}. Se conservan {len(result['documented_behaviors'])} observaciones documentadas y {len(result['counterevidence'])} entradas de contraevidencia.",
        f"La abstinencia figura {label(sexual['abstinence'])}; el celibato elegido figura {label(sexual['celibacy'])}. Las dimensiones conductual, emocional, erótica y ontológica se evalúan separadamente, sin equiparar ausencia sexual e integración.",
        f"La correspondencia astrológica tiene estado {result['astrological_correspondence']['status']}, con {len(result['structural_roots'])} raíces estructurales verificadas y {len(result['temporal_activations'])} activaciones temporales admitidas. Las familias simbólicas son temas interpretativos; la independencia procede de las raíces y dependencias declaradas.",
        "Retirada vestal es una hipótesis operativa de ALMAS. La doctrina histórica sobre Hestia, las vestales o la continencia se consulta por pasaje y tradición en el corpus; el uso contemporáneo sobre llamas gemelas requiere fuente propia. Ninguna de estas capas demuestra una identidad espiritual, un estado ajeno ni un desenlace de reunión.",
    ]


def evaluate_surrender_requests(raw: Any, *, documentary_events: Mapping[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """Adaptador opcional para M27 y canonical relacional, con atribución por sujeto."""
    if raw is None:
        return {}
    requests = _items(raw, "surrender_vestal_requests")
    output = {}
    event_registry = {event["event_id"]: event for event in (documentary_events or {}).get("events", [])}
    for original in requests:
        request = deepcopy(dict(original))
        observations = []
        for item in _items(request.get("observations", []), "observations"):
            observation = dict(item)
            if documentary_events is not None:
                event = event_registry.get(item.get("event_ref"))
                valid = event is not None and event.get("record_status") == "ACTIVE" and event.get("date_precision") in {"EXACT_DATE", "EXACT_DATETIME"} and event.get("documentary_quality_contract_met") is True and event.get("date_precision_contract_met") is True and event.get("fact_interpretation_separated") is True and request.get("subject_id") in event.get("subjects", [])
                if valid:
                    observation.update(date=event.get("date"), source_refs=event.get("source_refs"), documentary_quality=event.get("documentary_quality"), fact_interpretation_separated=True)
                    # Fechas datetime de M27 se reducen a día, nunca se inventa hora.
                    if event.get("date_precision") == "EXACT_DATETIME":
                        observation["date"] = str(event.get("date"))[:10]
                    if event.get("date_precision") not in {"EXACT_DATE", "EXACT_DATETIME"}:
                        observation["documentary_quality"] = "UNUSABLE"
                else:
                    observation["documentary_quality"] = "UNUSABLE"
            observations.append(observation)
        request["observations"] = observations
        result = assess_surrender_vestal(request)
        subject = result["subject_id"]
        if subject in output:
            raise ValueError(f"Solicitud duplicada de retirada vestal: {subject}")
        output[subject] = result
    return output
