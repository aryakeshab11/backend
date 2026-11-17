"""Experimental, non-diagnostic structured-feature builder.

This module deliberately does not define clinical cutoffs, infer diagnoses, calculate
risk scores, or make care recommendations. It must not be wired into production
agent responses until feature specifications and validation are approved.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


def _token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    if not token:
        raise ValueError("Feature names must contain letters or digits.")
    return token


def _unit(value: str) -> str:
    """Normalize unit spacing/case while preserving meaningful symbols like '%'."""
    normalized = " ".join(str(value).strip().casefold().split())
    if not normalized:
        raise ValueError("Units must not be empty.")
    return normalized


def engineer_descriptive_features(
    record: Mapping[str, Any],
    *,
    approved_age_cutpoints: Sequence[float] | None = None,
    approved_lab_units: Mapping[str, Iterable[str]] | None = None,
    approved_symptoms: Iterable[str] = (),
    approved_symptom_combinations: Iterable[Sequence[str]] = (),
) -> dict[str, float | str | int]:
    """Build descriptive features from explicitly approved schema inputs.

    Cutpoints, lab names/units, symptoms, and symptom combinations must come from
    a separately reviewed feature specification. No defaults encode clinical
    thresholds. Values are not interpreted as normal/abnormal or low/high.
    """
    features: dict[str, float | str | int] = {}

    if "age_years" in record and record["age_years"] is not None:
        age = float(record["age_years"])
        if not math.isfinite(age) or age < 0:
            raise ValueError("age_years must be a finite, non-negative number.")
        features["age_years"] = age
        if approved_age_cutpoints is not None:
            cutpoints = tuple(float(point) for point in approved_age_cutpoints)
            if any(not math.isfinite(point) for point in cutpoints):
                raise ValueError("Age cutpoints must be finite numbers.")
            if tuple(sorted(set(cutpoints))) != cutpoints:
                raise ValueError("Age cutpoints must be unique and strictly increasing.")
            band = sum(age >= point for point in cutpoints)
            features["age_band_index"] = int(band)

    approved_units = {
        _token(name): {_unit(unit) for unit in units}
        for name, units in (approved_lab_units or {}).items()
    }
    labs = record.get("labs", {})
    if labs is not None and not isinstance(labs, Mapping):
        raise ValueError("labs must be a mapping of test names to value/unit objects.")
    for name, observation in (labs or {}).items():
        lab_name = _token(str(name))
        if lab_name not in approved_units:
            raise ValueError(f"Lab feature is not in the approved schema: {lab_name}")
        if not isinstance(observation, Mapping) or "value" not in observation or "unit" not in observation:
            raise ValueError(f"Lab {lab_name} must include value and unit.")
        unit = _unit(observation["unit"])
        if unit not in approved_units[lab_name]:
            raise ValueError(f"Unit is not approved for lab {lab_name}: {unit}")
        value = float(observation["value"])
        if not math.isfinite(value):
            raise ValueError(f"Lab value for {lab_name} must be finite.")
        features[f"lab_{lab_name}_value"] = value
        features[f"lab_{lab_name}_unit"] = unit

    symptom_allowlist = {_token(item) for item in approved_symptoms}
    supplied_symptoms = record.get("symptoms", ()) or ()
    if isinstance(supplied_symptoms, (str, bytes)):
        raise ValueError("symptoms must be a collection of symptom names, not a string.")
    present = {_token(str(item)) for item in supplied_symptoms}
    unknown = present - symptom_allowlist
    if unknown:
        raise ValueError(f"Symptoms are not in the approved schema: {sorted(unknown)}")
    for symptom in sorted(symptom_allowlist):
        features[f"symptom_{symptom}"] = int(symptom in present)

    for combination in approved_symptom_combinations:
        members = tuple(_token(item) for item in combination)
        if len(members) < 2 or len(set(members)) != len(members):
            raise ValueError("Approved symptom combinations need at least two unique members.")
        if not set(members).issubset(symptom_allowlist):
            raise ValueError("Every symptom combination member must be allowlisted.")
        combo_name = "_and_".join(sorted(members))
        features[f"symptom_combo_{combo_name}"] = int(set(members).issubset(present))

    return features
