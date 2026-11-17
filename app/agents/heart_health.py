from __future__ import annotations


def build_heart_health_response(message: str, goals: list[str] | None = None) -> str:
    goals_text = ", ".join(goals) if goals else "cardiovascular health"
    return (
        f"Heart health coaching: support {goals_text} with steady activity, blood pressure awareness, low-sodium habits, and stress reduction. "
        f"For your question — '{message}' — a consistent plan is usually more effective than major changes. "
        "This is general wellness guidance and should be discussed with a clinician when symptoms or risk factors worsen."
    )
