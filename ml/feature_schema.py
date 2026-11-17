"""Proposed per-agent feature schemas; clinical approval is intentionally pending.

These allowlists are engineering scaffolds only. They are not clinical guidance,
validated predictors, medical-device specifications, or production-ready features.
No ranges, age cutpoints, score thresholds, or recommendations are encoded.
"""

from __future__ import annotations

from typing import TypedDict


class AgentFeatureSchema(TypedDict):
    approval_status: str
    age_cutpoints: None
    lab_units: dict[str, tuple[str, ...]]
    symptoms: tuple[str, ...]
    symptom_combinations: tuple[tuple[str, ...], ...]


# Candidate schema for product/clinical review only. Units are canonical labels;
# no value is classified or interpreted by the feature builder.
TUNA_DIABETES_SCHEMA: AgentFeatureSchema = {
    "approval_status": "proposed_not_clinically_approved",
    "age_cutpoints": None,
    "lab_units": {
        "hba1c": ("%", "mmol/mol"),
        "fasting_glucose": ("mg/dl", "mmol/l"),
        "random_glucose": ("mg/dl", "mmol/l"),
    },
    "symptoms": (
        "blurred_vision",
        "fatigue",
        "frequent_urination",
        "increased_thirst",
        "slow_healing_wounds",
        "unintentional_weight_change",
    ),
    "symptom_combinations": (),
}

SUNA_HEART_HEALTH_SCHEMA: AgentFeatureSchema = {
    "approval_status": "proposed_not_clinically_approved",
    "age_cutpoints": None,
    "lab_units": {
        "hdl_cholesterol": ("mg/dl", "mmol/l"),
        "ldl_cholesterol": ("mg/dl", "mmol/l"),
        "triglycerides": ("mg/dl", "mmol/l"),
    },
    "symptoms": (
        "chest_discomfort",
        "dizziness",
        "fatigue",
        "palpitations",
        "shortness_of_breath",
        "swelling",
    ),
    "symptom_combinations": (),
}

# Muna is intentionally omitted until its product domain is confirmed.
AGENT_FEATURE_SCHEMAS = {
    "tuna": TUNA_DIABETES_SCHEMA,
    "suna": SUNA_HEART_HEALTH_SCHEMA,
}
