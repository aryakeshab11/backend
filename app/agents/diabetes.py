from __future__ import annotations


def build_diabetes_response(message: str, goals: list[str] | None = None) -> str:
    goals_text = ", ".join(goals) if goals else "blood sugar management"
    return (
        f"Diabetes-focused coaching: focus on steady routines that support {goals_text}. "
        f"For your question — '{message}' — aim for regular meal timing, consistent activity, adequate hydration, and regular monitoring. "
        "This guidance is for general wellness support and is not a diagnosis or treatment plan."
    )
