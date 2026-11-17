from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.llm import call_llm
from app.qa import router as qa_router

app = FastAPI(title="AI-Health-Coach API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qa_router)


class ChatRequest(BaseModel):
    message: str
    goals: list[str] = []
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "AI-Health-Coach API"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message is required.")

    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    reply = call_llm(
        request.message.strip(),
        goals=request.goals,
        context=request.context,
        model=model_name,
    )
    return ChatResponse(reply=reply, model=model_name)
