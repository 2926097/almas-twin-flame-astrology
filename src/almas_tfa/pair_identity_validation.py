from __future__ import annotations

import hashlib
import hmac
import json
from functools import lru_cache
from importlib.resources import files
from typing import Any, Mapping, Sequence

from .discriminant_validation import wilson_interval


POLICY_RESOURCE = "data/pair-identity-validation-policy.json"
POLICY_ID = "ALMAS_PAIR_IDENTITY_VALIDATION_V1"

DECLARED_MATCHED_DYAD = "DECLARED_MATCHED_DYAD"
CROSS_DYAD_OPPOSITE_POLARITY = "CROSS_DYAD_OPPOSITE_POLARITY"
CROSS_DYAD_SAME_POLARITY_DF = "CROSS_DYAD_SAME_POLARITY_DF"
CROSS_DYAD_SAME_POLARITY_DM = "CROSS_DYAD_SAME_POLARITY_DM"
ORDINARY_CONTROL = "ORDINARY_CONTROL"

ALLOWED_STRATA = {
    DECLARED_MATCHED_DYAD,
    CROSS_DYAD_OPPOSITE_POLARITY,
    CROSS_DYAD_SAME_POLARITY_DF,
    CROSS_DYAD_SAME_POLARITY_DM,
    ORDINARY_CONTROL,
}


@lru_cache(maxsize=1)
def load_pair_identity_validation_policy() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(POLICY_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def _require_nonempty_string(value: Any, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}: se requiere string no vacío.")
    return value.strip()


def _hmac_id(secret: str, *, namespace: str, raw: str, prefix: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{namespace}|{raw}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:20]
    return f"{prefix}-{digest.upper()}"


def _validated_dyads(dyads: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    if not isinstance(dyads, Sequence) or isinstance(dyads, (str, bytes)):
        raise ValueError("dyads debe ser una secuencia.")
    if len(dyads) < 2:
        raise ValueError("Se requieren al menos dos díadas para construir hard negatives.")

    normalized: list[dict[str, str]] = []
    seen_dyads: set[str] = set()
    seen_subjects: set[str] = set()

    for index, item in enumerate(dyads):
        if not isinstance(item, Mapping):
            raise ValueError(f"dyads[{index}] debe ser un objeto.")

        allowed = {"dyad_ref", "df_ref", "dm_ref"}
        extra = set(item) - allowed
        if extra:
            raise ValueError(
                f"dyads[{index}] contiene campos no permitidos en el constructor ciego: "
                + ", ".join(sorted(str(key) for key in extra))
            )

        dyad_ref = _require_nonempty_string(
            item.get("dyad_ref"), name=f"dyads[{index}].dyad_ref"
        )
        df_ref = _require_nonempty_string(
            item.get("df_ref"), name=f"dyads[{index}].df_ref"
        )
        dm_ref = _require_nonempty_string(
            item.get("dm_ref"), name=f"dyads[{index}].dm_ref"
        )

        if dyad_ref in seen_dyads:
            raise ValueError(f"dyad_ref duplicado: {dyad_ref}.")
        for subject_ref in (df_ref, dm_ref):
            if subject_ref in seen_subjects:
                raise ValueError(
                    f"subject_ref reutilizado entre díadas: {subject_ref}."
                )
            seen_subjects.add(subject_ref)
        seen_dyads.add(dyad_ref)
        normalized.append(
            {"dyad_ref": dyad_ref, "df_ref": df_ref, "dm_ref": dm_ref}
        )

    return normalized


def build_blinded_pair_identity_matrix(
    dyads: Sequence[Mapping[str, Any]],
    *,
    blinding_secret: str,
    cross_rotation: int = 1,
    include_same_polarity: bool = True,
) -> dict[str, Any]:
    """Construye pares ciegos y truth sellado para identidad diádica.

    Esta función pertenece al rol custodio. blinded_pairs puede entregarse
    al pipeline estructural; sealed_truth debe permanecer separado hasta el
    reveal. Las referencias originales no aparecen en blinded_pairs.
    """

    secret = _require_nonempty_string(blinding_secret, name="blinding_secret")
    normalized = _validated_dyads(dyads)
    n = len(normalized)

    if not isinstance(cross_rotation, int) or isinstance(cross_rotation, bool):
        raise ValueError("cross_rotation debe ser entero.")
    rotation = cross_rotation % n
    if rotation == 0:
        raise ValueError(
            "cross_rotation debe producir una permutación sin puntos fijos."
        )

    if include_same_polarity and n % 2 != 0:
        raise ValueError(
            "La matriz same-polarity sin reutilización exige un número par de díadas."
        )

    subject_ids: dict[str, str] = {}
    dyad_ids: dict[str, str] = {}
    for item in normalized:
        dyad_ids[item["dyad_ref"]] = _hmac_id(
            secret,
            namespace="dyad",
            raw=item["dyad_ref"],
            prefix="D",
        )
        for key in ("df_ref", "dm_ref"):
            ref = item[key]
            subject_ids[ref] = _hmac_id(
                secret,
                namespace="subject",
                raw=ref,
                prefix="S",
            )

    raw_records: list[dict[str, Any]] = []

    def add_record(
        *,
        a_ref: str,
        b_ref: str,
        stratum: str,
        declared_match: bool,
        a_dyad_ref: str,
        b_dyad_ref: str,
        polarity_pattern: str,
        query_ref: str | None = None,
    ) -> None:
        a_id = subject_ids[a_ref]
        b_id = subject_ids[b_ref]
        canonical_pair = "|".join(sorted((a_id, b_id)))
        pair_id = _hmac_id(
            secret,
            namespace="pair",
            raw=canonical_pair,
            prefix="P",
        )
        raw_records.append(
            {
                "pair_id": pair_id,
                "subject_a_id": a_id,
                "subject_b_id": b_id,
                "stratum": stratum,
                "declared_match": declared_match,
                "subject_a_dyad_id": dyad_ids[a_dyad_ref],
                "subject_b_dyad_id": dyad_ids[b_dyad_ref],
                "polarity_pattern": polarity_pattern,
                "query_subject_id": (
                    subject_ids[query_ref] if query_ref is not None else None
                ),
            }
        )

    for item in normalized:
        add_record(
            a_ref=item["df_ref"],
            b_ref=item["dm_ref"],
            stratum=DECLARED_MATCHED_DYAD,
            declared_match=True,
            a_dyad_ref=item["dyad_ref"],
            b_dyad_ref=item["dyad_ref"],
            polarity_pattern="DF_DM",
            query_ref=item["df_ref"],
        )

    for index, item in enumerate(normalized):
        other = normalized[(index + rotation) % n]
        add_record(
            a_ref=item["df_ref"],
            b_ref=other["dm_ref"],
            stratum=CROSS_DYAD_OPPOSITE_POLARITY,
            declared_match=False,
            a_dyad_ref=item["dyad_ref"],
            b_dyad_ref=other["dyad_ref"],
            polarity_pattern="DF_DM",
            query_ref=item["df_ref"],
        )

    if include_same_polarity:
        for start in range(0, n, 2):
            left = normalized[start]
            right = normalized[start + 1]
            add_record(
                a_ref=left["df_ref"],
                b_ref=right["df_ref"],
                stratum=CROSS_DYAD_SAME_POLARITY_DF,
                declared_match=False,
                a_dyad_ref=left["dyad_ref"],
                b_dyad_ref=right["dyad_ref"],
                polarity_pattern="DF_DF",
            )
            add_record(
                a_ref=left["dm_ref"],
                b_ref=right["dm_ref"],
                stratum=CROSS_DYAD_SAME_POLARITY_DM,
                declared_match=False,
                a_dyad_ref=left["dyad_ref"],
                b_dyad_ref=right["dyad_ref"],
                polarity_pattern="DM_DM",
            )

    if len({record["pair_id"] for record in raw_records}) != len(raw_records):
        raise ValueError("La matriz produjo pair_id duplicados.")

    blinded_pairs = [
        {
            "pair_id": record["pair_id"],
            "subject_a_id": record["subject_a_id"],
            "subject_b_id": record["subject_b_id"],
        }
        for record in raw_records
    ]
    blinded_pairs.sort(key=lambda item: item["pair_id"])

    sealed_records = [
        {
            "pair_id": record["pair_id"],
            "stratum": record["stratum"],
            "declared_match": record["declared_match"],
            "subject_a_dyad_id": record["subject_a_dyad_id"],
            "subject_b_dyad_id": record["subject_b_dyad_id"],
            "polarity_pattern": record["polarity_pattern"],
            "query_subject_id": record["query_subject_id"],
        }
        for record in raw_records
    ]
    sealed_records.sort(key=lambda item: item["pair_id"])

    counts = {
        stratum: sum(
            1 for item in sealed_records if item["stratum"] == stratum
        )
        for stratum in sorted(ALLOWED_STRATA)
        if any(item["stratum"] == stratum for item in sealed_records)
    }

    return {
        "policy_id": POLICY_ID,
        "custodian_only": True,
        "blinded_pairs": blinded_pairs,
        "sealed_truth": {
            "records": sealed_records,
            "truth_must_remain_hidden_until_reveal": True,
        },
        "matrix_summary": {
            "dyad_count": n,
            "pair_count": len(raw_records),
            "stratum_counts": counts,
            "primary_positive_stratum": DECLARED_MATCHED_DYAD,
            "primary_hard_negative_stratum": CROSS_DYAD_OPPOSITE_POLARITY,
            "same_polarity_included": include_same_polarity,
            "cross_rotation": rotation,
        },
        "metaphysical_ground_truth": False,
    }


def _score_map(scores: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    if not isinstance(scores, Sequence) or isinstance(scores, (str, bytes)):
        raise ValueError("scores debe ser una secuencia.")

    output: dict[str, float] = {}
    for index, item in enumerate(scores):
        if not isinstance(item, Mapping):
            raise ValueError(f"scores[{index}] debe ser un objeto.")
        if set(item) - {"pair_id", "score"}:
            raise ValueError("scores sólo admite pair_id y score en el reveal.")

        pair_id = _require_nonempty_string(
            item.get("pair_id"), name=f"scores[{index}].pair_id"
        )
        raw_score = item.get("score")
        if (
            isinstance(raw_score, bool)
            or not isinstance(raw_score, (int, float))
        ):
            raise ValueError(f"scores[{index}].score debe ser numérico.")
        if pair_id in output:
            raise ValueError(f"score duplicado para {pair_id}.")
        output[pair_id] = float(raw_score)

    return output


def _auc(
    positive_scores: Sequence[float],
    negative_scores: Sequence[float],
) -> float:
    if not positive_scores or not negative_scores:
        raise ValueError("AUC requiere positivos y negativos.")

    wins = 0.0
    total = len(positive_scores) * len(negative_scores)
    for positive in positive_scores:
        for negative in negative_scores:
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return wins / total


def _metrics_for_stratum(
    positive_scores: Sequence[float],
    negative_scores: Sequence[float],
    *,
    threshold: float,
) -> dict[str, Any]:
    tp = sum(1 for score in positive_scores if score >= threshold)
    fn = len(positive_scores) - tp
    fp = sum(1 for score in negative_scores if score >= threshold)
    tn = len(negative_scores) - fp

    sensitivity = tp / len(positive_scores)
    specificity = tn / len(negative_scores)
    sensitivity_ci_lower, sensitivity_ci_upper = wilson_interval(
        tp, len(positive_scores)
    )
    specificity_ci_lower, specificity_ci_upper = wilson_interval(
        tn, len(negative_scores)
    )
    _, false_specificity_ci_upper = wilson_interval(
        fp, len(negative_scores)
    )

    return {
        "positive_count": len(positive_scores),
        "negative_count": len(negative_scores),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "balanced_accuracy": (sensitivity + specificity) / 2.0,
        "sensitivity_ci95": [
            sensitivity_ci_lower,
            sensitivity_ci_upper,
        ],
        "specificity_ci95": [
            specificity_ci_lower,
            specificity_ci_upper,
        ],
        "false_specificity_rate": fp / len(negative_scores),
        "false_specificity_ci95_upper": false_specificity_ci_upper,
        "roc_auc": _auc(positive_scores, negative_scores),
    }


def validate_partition_disjointness(
    partitions: Mapping[str, Sequence[str]],
) -> dict[str, Any]:
    if not isinstance(partitions, Mapping) or len(partitions) < 2:
        raise ValueError("partitions debe contener al menos dos particiones.")

    seen: dict[str, str] = {}
    counts: dict[str, int] = {}

    for partition_id, raw_subjects in partitions.items():
        pid = _require_nonempty_string(partition_id, name="partition_id")
        if (
            not isinstance(raw_subjects, Sequence)
            or isinstance(raw_subjects, (str, bytes))
        ):
            raise ValueError(f"{pid}: subjects debe ser una secuencia.")

        subjects: list[str] = []
        for raw in raw_subjects:
            subject = _require_nonempty_string(
                raw, name=f"{pid}.subject"
            )
            if subject in subjects:
                raise ValueError(f"{pid}: subject duplicado {subject}.")
            other = seen.get(subject)
            if other is not None:
                raise ValueError(
                    f"Leakage de sujeto entre particiones: {subject} "
                    f"aparece en {other} y {pid}."
                )
            seen[subject] = pid
            subjects.append(subject)
        counts[pid] = len(subjects)

    return {
        "state": "DISJOINT",
        "partition_counts": counts,
        "shared_subject_count": 0,
    }


def evaluate_pair_identity_holdout(
    scores: Sequence[Mapping[str, Any]],
    sealed_truth: Mapping[str, Any],
    *,
    threshold: float,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalúa identidad diádica declarada después del reveal.

    El hard negative confirmatorio es siempre DF-DM cruzado para impedir que el
    sistema aprenda sólo polaridad. El resultado valida, como máximo,
    discriminación operacional de la etiqueta documental de díada.
    """

    policy = policy or load_pair_identity_validation_policy()
    if policy.get("policy_id") != POLICY_ID:
        raise ValueError("Política de identidad diádica desconocida.")

    if isinstance(threshold, bool) or not isinstance(
        threshold, (int, float)
    ):
        raise ValueError("threshold debe ser numérico.")
    threshold = float(threshold)

    if not isinstance(sealed_truth, Mapping):
        raise ValueError("sealed_truth debe ser un objeto.")
    records = sealed_truth.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("sealed_truth.records no puede estar vacío.")

    truth_by_pair: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            raise ValueError(f"sealed_truth.records[{index}] inválido.")

        pair_id = _require_nonempty_string(
            raw.get("pair_id"), name="pair_id"
        )
        stratum = raw.get("stratum")
        if stratum not in ALLOWED_STRATA:
            raise ValueError(f"stratum no reconocido: {stratum!r}.")

        declared_match = raw.get("declared_match")
        if not isinstance(declared_match, bool):
            raise ValueError("declared_match debe ser booleano.")
        if (stratum == DECLARED_MATCHED_DYAD) != declared_match:
            raise ValueError("declared_match contradice el stratum.")

        if pair_id in truth_by_pair:
            raise ValueError(f"pair_id duplicado en truth: {pair_id}.")
        truth_by_pair[pair_id] = dict(raw)

    scores_by_pair = _score_map(scores)
    if set(scores_by_pair) != set(truth_by_pair):
        missing = sorted(set(truth_by_pair) - set(scores_by_pair))
        extra = sorted(set(scores_by_pair) - set(truth_by_pair))
        raise ValueError(
            f"Cobertura de scores no exacta; missing={missing}, extra={extra}."
        )

    positives = [
        scores_by_pair[pair_id]
        for pair_id, item in truth_by_pair.items()
        if item["stratum"] == DECLARED_MATCHED_DYAD
    ]
    primary_negatives = [
        scores_by_pair[pair_id]
        for pair_id, item in truth_by_pair.items()
        if item["stratum"] == CROSS_DYAD_OPPOSITE_POLARITY
    ]
    if not positives or not primary_negatives:
        raise ValueError(
            "Faltan positivos declarados o hard negatives DF-DM cruzados."
        )

    metrics_by_stratum: dict[str, Any] = {}
    for stratum in (
        CROSS_DYAD_OPPOSITE_POLARITY,
        CROSS_DYAD_SAME_POLARITY_DF,
        CROSS_DYAD_SAME_POLARITY_DM,
        ORDINARY_CONTROL,
    ):
        negatives = [
            scores_by_pair[pair_id]
            for pair_id, item in truth_by_pair.items()
            if item["stratum"] == stratum
        ]
        if negatives:
            metrics_by_stratum[stratum] = _metrics_for_stratum(
                positives,
                negatives,
                threshold=threshold,
            )

    primary = metrics_by_stratum[CROSS_DYAD_OPPOSITE_POLARITY]
    minimums = policy["confirmatory_gate"]["minimums"]
    passed = (
        primary["sensitivity_ci95"][0]
        >= float(minimums["sensitivity_ci95_lower"])
        and primary["specificity_ci95"][0]
        >= float(minimums["specificity_ci95_lower"])
        and primary["balanced_accuracy"]
        >= float(minimums["balanced_accuracy"])
        and primary["false_specificity_ci95_upper"]
        <= float(minimums["false_specificity_ci95_upper"])
    )

    query_groups: dict[str, dict[str, float]] = {}
    for pair_id, item in truth_by_pair.items():
        query = item.get("query_subject_id")
        if not isinstance(query, str) or not query:
            continue
        if item["stratum"] not in {
            DECLARED_MATCHED_DYAD,
            CROSS_DYAD_OPPOSITE_POLARITY,
        }:
            continue
        query_groups.setdefault(query, {})[
            str(item["stratum"])
        ] = scores_by_pair[pair_id]

    complete_queries = 0
    true_wins = 0
    ties = 0
    for values in query_groups.values():
        if (
            DECLARED_MATCHED_DYAD not in values
            or CROSS_DYAD_OPPOSITE_POLARITY not in values
        ):
            continue
        complete_queries += 1
        true_score = values[DECLARED_MATCHED_DYAD]
        cross_score = values[CROSS_DYAD_OPPOSITE_POLARITY]
        if true_score > cross_score:
            true_wins += 1
        elif true_score == cross_score:
            ties += 1

    paired_concordance = (
        (true_wins + 0.5 * ties) / complete_queries
        if complete_queries
        else None
    )

    return {
        "policy_id": POLICY_ID,
        "evaluation_scope": "DECLARED_MATCHED_DYAD_DISCRIMINATION",
        "primary_positive_stratum": DECLARED_MATCHED_DYAD,
        "primary_hard_negative_stratum": (
            CROSS_DYAD_OPPOSITE_POLARITY
        ),
        "threshold": threshold,
        "score_direction": "HIGHER_IS_MORE_MATCHED",
        "metrics_by_negative_stratum": metrics_by_stratum,
        "paired_query_diagnostics": {
            "complete_query_count": complete_queries,
            "true_pair_wins": true_wins,
            "ties": ties,
            "paired_concordance": paired_concordance,
        },
        "confirmatory_gate": {
            "state": (
                "PASS_OPERATIONAL_GATE"
                if passed
                else "FAIL_OPERATIONAL_GATE"
            ),
            "passed": passed,
            "primary_hard_negative_only": True,
            "replication_required": True,
            "l3_promotion_authorized": False,
            "ontology_activation": False,
        },
        "tf_phenotype_equals_pair_identity": False,
        "declared_match_is_metaphysical_ground_truth": False,
        "metaphysical_probability": False,
    }
