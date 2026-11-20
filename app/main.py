from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agents.devops_agent import run_devops_agent

from app.llm import call_llm
from app.qa import router as qa_router

router = APIRouter(prefix="/devops", tags=["devops"])

class DevOpsRequest(BaseModel):
    prompt: str
    model: str = "gpt-5-mini"

@router.post("/assist")
def devops_assist(payload: DevOpsRequest):
    try:
        reply = run_devops_agent(prompt=payload.prompt, model=payload.model)
        return {"response": reply}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

app = FastAPI(title="AI-Health-Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qa_router)
app.include_router(router)

class ChatRequest(BaseModel):
    message: str
    goals: list[str] = []
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "AI-Health-Assistant API"}


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
