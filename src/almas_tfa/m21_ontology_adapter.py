from __future__ import annotations

from typing import Any, Mapping

from .ontological_discriminator import discriminate_ontology


M21_ONTOLOGY_INPUT_KEY = "ontological_discriminator_input"


def evaluate_m21_ontological_sublayer(
    raw_input: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Evalúa la subcapa ontológica opcional de M21.

    La ausencia de ontological_discriminator_input conserva exactamente el
    comportamiento histórico de M21. La subcapa no consume IDD, IEM ni scores.
    """

    config = raw_input.get(M21_ONTOLOGY_INPUT_KEY)
    if config is None:
        return None
    if not isinstance(config, Mapping):
        raise ValueError(
            "ontological_discriminator_input debe ser un objeto."
        )

    observations = config.get("observations", [])
    if observations is None:
        observations = []
    if not isinstance(observations, (list, tuple)):
        raise ValueError(
            "ontological_discriminator_input.observations debe ser una lista."
        )

    models = config.get("models")
    if models is not None and not isinstance(models, (list, tuple)):
        raise ValueError(
            "ontological_discriminator_input.models debe ser una lista."
        )

    mode = str(config.get("mode") or "CONFIRMATORY").upper()

    minimum_data_evaluable = config.get("minimum_data_evaluable", True)
    if not isinstance(minimum_data_evaluable, bool):
        raise ValueError(
            "ontological_discriminator_input.minimum_data_evaluable debe ser booleano."
        )

    pair_coverage = config.get("pair_coverage")
    if pair_coverage is not None and not isinstance(pair_coverage, Mapping):
        raise ValueError(
            "ontological_discriminator_input.pair_coverage debe ser un objeto."
        )

    return discriminate_ontology(
        observations,
        models=models,
        mode=mode,
        minimum_data_evaluable=minimum_data_evaluable,
        pair_coverage=pair_coverage,
    )
