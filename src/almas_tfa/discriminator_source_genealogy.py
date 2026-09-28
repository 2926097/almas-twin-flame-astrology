from __future__ import annotations

import copy
import json
from functools import lru_cache
from importlib.resources import files
from typing import Any, Mapping


RESOURCE = "data/discriminator-source-genealogy.json"


@lru_cache(maxsize=1)
def load_discriminator_source_genealogy() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def _source_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    snapshots = registry.get("source_snapshots")
    if not isinstance(snapshots, list):
        raise ValueError("source_snapshots debe ser una lista.")

    result: dict[str, Mapping[str, Any]] = {}
    for source in snapshots:
        if not isinstance(source, Mapping):
            raise ValueError("source_snapshots contiene una entrada inválida.")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("source_snapshots contiene id inválido.")
        if source_id in result:
            raise ValueError(f"source_id duplicado: {source_id}")
        result[source_id] = source
    return result


def _record_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    records = registry.get("records")
    if not isinstance(records, list):
        raise ValueError("records debe ser una lista.")

    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("records contiene una entrada inválida.")
        discriminator_id = record.get("discriminator_id")
        if not isinstance(discriminator_id, str) or not discriminator_id:
            raise ValueError("registro sin discriminator_id.")
        if discriminator_id in result:
            raise ValueError(f"discriminator_id duplicado: {discriminator_id}")
        result[discriminator_id] = record
    return result


def get_discriminator_source_genealogy(
    discriminator_id: str,
    *,
    registry: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    registry = registry or load_discriminator_source_genealogy()
    records = _record_map(registry)
    if discriminator_id not in records:
        raise KeyError(discriminator_id)
    return records[discriminator_id]


def _resolved_source_usage(
    record: Mapping[str, Any],
    source_map: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    usage = record.get("source_usage", [])
    if not isinstance(usage, list):
        raise ValueError("source_usage debe ser una lista.")

    for item in usage:
        if not isinstance(item, Mapping):
            raise ValueError("source_usage contiene una entrada inválida.")
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or source_id not in source_map:
            raise ValueError(
                f"source_usage referencia source_id desconocido: {source_id}"
            )
        source = source_map[source_id]
        result.append(
            {
                "source_id": source_id,
                "priority": source.get("priority"),
                "source_role": source.get("source_role"),
                "tradition": source.get("tradition"),
                "author": source.get("author"),
                "work": source.get("work"),
                "date": source.get("date"),
                "date_note": source.get("date_note"),
                "passage": source.get("passage"),
                "pages": source.get("pages"),
                "verification_status": source.get("verification_status"),
                "verification_anchor": source.get("verification_anchor"),
                "verification_anchor_type": source.get(
                    "verification_anchor_type"
                ),
                "verification_anchor_url": source.get(
                    "verification_anchor_url"
                ),
                "evidence_scope": source.get("evidence_scope"),
                "relation": item.get("relation"),
                "concept_refs": copy.deepcopy(item.get("concept_refs", [])),
                "support_indexes": copy.deepcopy(
                    item.get("support_indexes", [])
                ),
                "does_not_support_indexes": copy.deepcopy(
                    item.get("does_not_support_indexes", [])
                ),
                "direct_case_evidence": False,
                "ontological_validation": False,
            }
        )
    return result


def build_discriminator_source_genealogy_reporting(
    *,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or load_discriminator_source_genealogy()
    source_map = _source_map(registry)
    records = _record_map(registry)

    output_records: list[dict[str, Any]] = []
    for discriminator_id in sorted(records):
        record = records[discriminator_id]
        resolved_sources = _resolved_source_usage(record, source_map)
        output_records.append(
            {
                "discriminator_id": discriminator_id,
                "derived_from": copy.deepcopy(record.get("derived_from", [])),
                "provenance_class": record.get("provenance_class"),
                "epistemic_class": record.get("epistemic_class"),
                "epistemic_ceiling": record.get("epistemic_ceiling"),
                "source_refs": [
                    item["source_id"] for item in resolved_sources
                ],
                "source_priorities": sorted(
                    {
                        str(item["priority"])
                        for item in resolved_sources
                        if item.get("priority") is not None
                    }
                ),
                "source_roles": sorted(
                    {
                        str(item["source_role"])
                        for item in resolved_sources
                        if item.get("source_role") is not None
                    }
                ),
                "traditions": sorted(
                    {
                        str(item["tradition"])
                        for item in resolved_sources
                        if item.get("tradition") is not None
                    }
                ),
                "sources": resolved_sources,
                "required_genealogy_edges": copy.deepcopy(
                    record.get("required_genealogy_edges", [])
                ),
                "forbidden_equivalences": copy.deepcopy(
                    record.get("forbidden_equivalences", [])
                ),
                "operationalization_note": record.get(
                    "operationalization_note"
                ),
                "source_count_adds_weight": False,
                "source_priority_adds_ontological_weight": False,
                "cross_tradition_identity_allowed": False,
                "direct_case_evidence": False,
                "can_change_case_classification": False,
                "can_raise_irc": False,
            }
        )

    return {
        "reporting_version": "1.0.0",
        "reporting_kind": "DISCRIMINATOR_SOURCE_GENEALOGY",
        "authority": registry.get("authority"),
        "methodological_provenance_only": True,
        "ontological_inference_allowed": False,
        "source_count_adds_weight": False,
        "source_priority_adds_ontological_weight": False,
        "cross_tradition_identity_allowed": False,
        "records": output_records,
    }
