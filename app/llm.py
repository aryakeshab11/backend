from __future__ import annotations

import os
from collections.abc import Iterable

from openai import OpenAI


def get_api_key() -> str | None:
    return os.getenv("OPEN_AI_KEY") or os.getenv("OPENAI_API_KEY")


def call_llm(
    message: str,
    goals: Iterable[str] | None = None,
    context: dict | None = None,
    model: str | None = None,
) -> str:
    """Generate a coaching response using OpenAI when configured; otherwise fall back to a local stub."""
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_key = get_api_key()

    system_prompt = (
        "You are a helpful, friendly, and safety-conscious health coach. "
        "Provide general wellness guidance, avoid making clinical diagnoses, and encourage professional care when appropriate. "
        "When uncertain, include a brief disclaimer."
    )

    user_prompt = f"Message: {message}"
    if goals:
        user_prompt += f"\nGoals: {', '.join(goals)}"
    if context:
        user_prompt += f"\nContext: {context}"

    if not api_key:
        stub = f"[stubbed LLM response] {message}"
        if goals:
            stub += f" (goals: {', '.join(goals)})"
        return stub

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        content = response.choices[0].message.content
        return content.strip() if content else "[empty response from LLM]"
    except Exception as exc:  # pragma: no cover - best effort fallback
        return f"[llm-error] {exc}"
