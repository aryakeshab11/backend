from __future__ import annotations

from typing import Any

from .diabetes import build_diabetes_response
from .general_wellness import build_general_wellness_response
from .heart_health import build_heart_health_response
from .safety import detect_urgent_symptoms, get_safety_notice


def route_message(message: str, selected_agent: str | None = None, user_profile: dict[str, Any] | None = None) -> str:
    """Return the most appropriate agent name for the message and user profile."""
    text = (message or "").lower()
    profile = user_profile or {}
    focus = str(profile.get("health_focus") or profile.get("main_health_focus") or "").lower()

    if detect_urgent_symptoms(message):
        return "safety_triage"
    if selected_agent:
        return selected_agent.lower()
    if "diabetes" in focus or any(token in text for token in ["blood sugar", "glucose", "diabetes", "a1c", "insulin"]):
        return "diabetes"
    if "heart" in focus or any(token in text for token in ["heart", "blood pressure", "cardio", "cholesterol", "cardiovascular"]):
        return "heart_health"
    if "cancer" in focus or any(token in text for token in ["cancer", "tumor", "oncology", "screening", "chemo", "radiation"]):
        return "muna"
    return "zuna"


def build_agent_response(
    message: str,
    selected_agent: str | None = None,
    user_profile: dict[str, Any] | None = None,
    goals: list[str] | None = None,
) -> tuple[str, str]:
    """Return (agent_name, agent_response)."""
    agent_name = route_message(message, selected_agent=selected_agent, user_profile=user_profile)

    # instant safety override before any specialist response
    safety_notice = get_safety_notice(message)
    if safety_notice:
        return "safety_triage", safety_notice

    if agent_name == "diabetes":
        return agent_name, build_diabetes_response(message, goals=goals or [])
    if agent_name == "heart_health":
        return agent_name, build_heart_health_response(message, goals=goals or [])
    if agent_name == "muna":
        return agent_name, (
            "Cancer-focused coaching: use a structured screening and symptom review process, track follow-ups, "
            "stay alert for significant changes, and discuss any new or worsening symptoms promptly with a clinician. "
            "This is general education and not a diagnosis."
        )
    return agent_name, build_general_wellness_response(message, goals=goals or [])
