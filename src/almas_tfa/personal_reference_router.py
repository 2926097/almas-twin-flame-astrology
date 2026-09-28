from __future__ import annotations

from copy import deepcopy
from importlib import resources
import json
from typing import Any, Mapping

from .personal_reporting import route_personal_reference_domains


ROUTER_RESOURCE = "personal-report-reference-router.json"
ROUTER_ID = "ALMAS_PERSONAL_REFERENCE_ROUTER_V1"


class PersonalReferenceRouterError(ValueError):
    pass


def load_personal_reference_router() -> dict[str, Any]:
    resource = resources.files("almas_tfa").joinpath(
        "data",
        ROUTER_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        router = json.load(handle)
    if router.get("router_id") != ROUTER_ID:
        raise PersonalReferenceRouterError(
            "Router de referencias personales desconocido."
        )
    return router


def _source_entries(
    source_registry: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    entries = source_registry.get("entries")
    if not isinstance(entries, list):
        raise PersonalReferenceRouterError(
            "source_registry.entries debe ser una lista."
        )

    output: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise PersonalReferenceRouterError(
                "Cada entrada de source_registry debe ser un objeto."
            )
        source_id = entry.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise PersonalReferenceRouterError(
                "Cada fuente debe declarar id."
            )
        if source_id in output:
            raise PersonalReferenceRouterError(
                f"source_id duplicado: {source_id}"
            )
        output[source_id] = entry
    return output


def route_personal_reference_sources(
    canonical: Mapping[str, Any],
    source_registry: Mapping[str, Any],
    *,
    router: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resuelve dominios activos contra source_ids ya registrados."""

    resolved_router = dict(
        router or load_personal_reference_router()
    )
    if resolved_router.get("router_id") != ROUTER_ID:
        raise PersonalReferenceRouterError(
            "router_id personal no reconocido."
        )
    domain_map = resolved_router.get("domains")
    if not isinstance(domain_map, Mapping):
        raise PersonalReferenceRouterError(
            "El router no declara domains."
        )

    sources = _source_entries(source_registry)
    requested_domains = route_personal_reference_domains(canonical)
    routed_domains: list[dict[str, Any]] = []
    all_source_ids: set[str] = set()
    gaps: list[str] = []

    for domain in requested_domains:
        config = domain_map.get(domain)
        if not isinstance(config, Mapping):
            raise PersonalReferenceRouterError(
                f"Dominio no registrado en router: {domain}"
            )

        source_ids = config.get("source_ids", [])
        if not isinstance(source_ids, list):
            raise PersonalReferenceRouterError(
                f"{domain}.source_ids debe ser una lista."
            )
        missing = sorted(
            source_id
            for source_id in source_ids
            if source_id not in sources
        )
        if missing:
            raise PersonalReferenceRouterError(
                f"{domain}: fuentes inexistentes en source-registry: "
                + ", ".join(missing)
            )

        status = config.get("status")
        if status == "SOURCE_GAP":
            gaps.append(domain)
        all_source_ids.update(str(source_id) for source_id in source_ids)

        routed_domains.append(
            {
                "domain": domain,
                "status": status,
                "epistemic_scope": list(
                    config.get("epistemic_scope", [])
                ),
                "source_ids": list(source_ids),
                "internal_refs": list(
                    config.get("internal_refs", [])
                ),
                "gap_reason": config.get("gap_reason"),
            }
        )

    return {
        "router_id": ROUTER_ID,
        "source_registry_version": source_registry.get(
            "registry_version"
        ),
        "domains": routed_domains,
        "source_ids": sorted(all_source_ids),
        "source_gaps": sorted(gaps),
    }


def enrich_personal_canonical_sources(
    canonical: Mapping[str, Any],
    source_registry: Mapping[str, Any],
    *,
    router: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Añade trazabilidad de fuentes sin alterar cálculo ni doctrina."""

    routing = route_personal_reference_sources(
        canonical,
        source_registry,
        router=router,
    )
    sources = _source_entries(source_registry)

    output = deepcopy(dict(canonical))
    existing = output.get("source_trace")
    if existing is None:
        trace: list[dict[str, Any]] = []
    elif isinstance(existing, list):
        trace = []
        for index, item in enumerate(existing):
            if not isinstance(item, Mapping):
                raise PersonalReferenceRouterError(
                    "canonical.source_trace contiene un elemento no objeto "
                    f"en índice {index}."
                )
            trace.append(deepcopy(dict(item)))
    else:
        raise PersonalReferenceRouterError(
            "canonical.source_trace debe ser una lista."
        )

    route_domains_by_source: dict[str, set[str]] = {}
    for domain in routing["domains"]:
        for source_id in domain["source_ids"]:
            route_domains_by_source.setdefault(
                source_id,
                set(),
            ).add(domain["domain"])

    trace_by_source_id: dict[str, dict[str, Any]] = {}
    for item in trace:
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            continue
        if source_id in trace_by_source_id:
            raise PersonalReferenceRouterError(
                f"source_id duplicado en canonical.source_trace: {source_id}"
            )
        trace_by_source_id[source_id] = item

    for source_id in routing["source_ids"]:
        routed_domains = route_domains_by_source.get(
            source_id,
            set(),
        )
        existing_item = trace_by_source_id.get(source_id)
        if existing_item is not None:
            current_domains = existing_item.get("route_domains", [])
            if current_domains is None:
                current_domains = []
            if not isinstance(current_domains, list) or any(
                not isinstance(domain, str) or not domain
                for domain in current_domains
            ):
                raise PersonalReferenceRouterError(
                    f"{source_id}.route_domains debe ser una lista de strings."
                )
            existing_item["route_domains"] = sorted(
                set(current_domains) | routed_domains
            )
            continue

        source = sources[source_id]
        item = {
            "source_id": source_id,
            "route_domains": sorted(routed_domains),
            "priority": source.get("priority"),
            "source_role": source.get("source_role"),
            "tradition": source.get("tradition"),
            "author": source.get("author"),
            "work": source.get("work"),
            "verification_status": source.get(
                "verification_status"
            ),
            "evidence_scope": source.get(
                "evidence_scope"
            ),
        }
        trace.append(item)
        trace_by_source_id[source_id] = item

    output["source_trace"] = trace
    return output
