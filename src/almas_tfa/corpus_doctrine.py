"""Atribución de pasajes y límites del corpus; nunca puntuación de una díada."""
from __future__ import annotations

from copy import deepcopy
from importlib.resources import files
import json
from typing import Any


def load_corpus_doctrine_policy() -> dict[str, Any]:
    return json.loads(files("almas_tfa").joinpath("data/corpus-doctrine-policy.json").read_text(encoding="utf-8"))


def _source_ids(source_ids: list[str], policy: dict[str, Any]) -> list[str]:
    known = {s["id"] for s in policy["source_snapshots"]}
    if not isinstance(source_ids, list) or any(not isinstance(s, str) or s not in known for s in source_ids):
        raise ValueError("La consulta requiere identificadores del corpus doctrinal empaquetado.")
    return sorted(set(source_ids))


def corpus_source_trace(source_ids: list[str]) -> dict[str, Any]:
    """Agrupar por familia conservadora; raíz desconocida no prueba independencia."""
    policy = load_corpus_doctrine_policy()
    selected = _source_ids(source_ids, policy)
    sources = {s["id"]: s for s in policy["source_snapshots"]}
    groups: dict[str, list[str]] = {}
    unresolved = []
    for ident in selected:
        root = sources[ident].get("dependency_root")
        if root is None:
            unresolved.append(ident)
        else:
            groups.setdefault(root, []).append(ident)
    return {
        "source_refs": selected,
        "dependency_groups": [{"dependency_root": root, "source_refs": refs} for root, refs in sorted(groups.items())],
        "unresolved_dependency_refs": unresolved,
        "independence_validated": False,
        "source_count_adds_weight": False,
    }


def assess_corpus_claim(concept_id: str, source_ids: list[str], *, scope: str = "DOCTRINAL_ATTRIBUTION", proposed_upgrade: str | None = None) -> dict[str, Any]:
    """SUPPORTED atribuye el concepto a pasajes consultados, no confirma su realidad."""
    policy = load_corpus_doctrine_policy()
    if concept_id not in policy["concept_ceilings"]:
        raise ValueError("Concepto desconocido.")
    if scope not in {"DOCTRINAL_ATTRIBUTION", "PROJECT_CORRESPONDENCE", "CASE_ONTOLOGY"}:
        raise ValueError("Alcance doctrinal desconocido.")
    if proposed_upgrade is not None and proposed_upgrade not in policy["forbidden_upgrades"]:
        raise ValueError("Promoción inferencial desconocida.")
    selected = _source_ids(source_ids, policy)
    sources = {s["id"]: s for s in policy["source_snapshots"]}
    assertions = [deepcopy(a) for a in policy["assertions"] if a["concept_id"] == concept_id and a["source_id"] in selected]
    usable = [a for a in assertions if sources[a["source_id"]]["verification_status"] == "VERIFIED_PRIMARY"
              and sources[a["source_id"]].get("evidence_scope") == "DOCTRINAL_CLAIM"
              and a["epistemic_class"] == "C_DOCTRINE"]
    support = any(a["polarity"] == "SUPPORTS" for a in usable)
    contra = any(a["polarity"] == "CONTRADICTS" for a in usable)
    # Hechos bilaterales/sexuales no pueden nacer de una cita histórica.
    factual = concept_id in {"CELIBACY_CHOSEN", "EXTERNAL_DYADIC_UNION", "EXTERNAL_ROMANTIC_REUNION"}
    if not selected or factual:
        status = "NOT_EVALUABLE"
    elif scope == "CASE_ONTOLOGY" or proposed_upgrade is not None:
        status = "INSUFFICIENT"
    elif scope == "PROJECT_CORRESPONDENCE":
        status = "COMPATIBLE" if assertions else "INSUFFICIENT"
    elif support and contra:
        status = "INSUFFICIENT"
    elif contra:
        status = "CONTRADICTED"
    elif support:
        status = "SUPPORTED"
    else:
        status = "INSUFFICIENT"
    return {
        "policy_id": policy["policy_id"], "concept_id": concept_id,
        "scope": scope, "status": status,
        "epistemic_class": "C_DOCTRINE" if scope == "DOCTRINAL_ATTRIBUTION" and usable else "E_PROJECT_HYPOTHESIS",
        "inferential_ceiling": policy["concept_ceilings"][concept_id],
        "assertions": assertions,
        "admissible_source_refs": sorted({a["source_id"] for a in usable}),
        "pending_or_indirect_source_refs": sorted(set(selected) - {a["source_id"] for a in usable}),
        "source_trace": corpus_source_trace(selected),
        "blocked_upgrades": [proposed_upgrade] if proposed_upgrade is not None else [],
        "ontology_effect": "NONE", "iem_modified": False, "pu_created": False, "l3_substituted": False,
    }
