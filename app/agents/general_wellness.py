from __future__ import annotations


def build_general_wellness_response(message: str, goals: list[str] | None = None) -> str:
    goals_text = ", ".join(goals) if goals else "your overall wellbeing"
    return (
        f"General wellness guidance: focus on one or two small, sustainable habits for {goals_text}. "
        f"For your question — '{message}' — start with a simple plan: sleep, hydration, movement, and stress reduction. "
        "If you want deeper support, I can help you build a short daily rhythm around your goals."
    )
