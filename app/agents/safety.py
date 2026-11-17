from __future__ import annotations

URGENT_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "trouble breathing",
    "fainting",
    "stroke",
    "severe headache",
    "severe weakness",
    "severe dizziness",
    "passing out",
    "cannot breathe",
    "unconscious",
    "arm pain",
    "pressure in chest",
]


def detect_urgent_symptoms(message: str) -> bool:
    if not message:
        return False
    text = message.lower()
    return any(keyword in text for keyword in URGENT_KEYWORDS)


def get_safety_notice(message: str) -> str | None:
    if not detect_urgent_symptoms(message):
        return None
    return (
        "This sounds urgent. If you are having severe chest pain, trouble breathing, fainting, or other emergency symptoms, "
        "seek immediate medical attention or call emergency services now. This is general information and is not a diagnosis."
    )
