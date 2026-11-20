from __future__ import annotations

import json
from pathlib import Path

#import faiss
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.llm import call_llm

router = APIRouter(prefix="/qa", tags=["qa"])


class QARequest(BaseModel):
    query: str
    k: int = 5


class QAResponse(BaseModel):
    answer: str
    sources: list[str]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = PROJECT_ROOT / "data" / "faiss.index"
METADATA_PATH = PROJECT_ROOT / "data" / "doc_metadata.json"


def _load_index():
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise HTTPException(status_code=503, detail="QA index not built yet. Run the index builder first.")
    index = faiss.read_index(str(INDEX_PATH))
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata


def _embed_query(query: str) -> np.ndarray:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)
    result = client.embeddings.create(model="text-embedding-3-small", input=[query])
    embedding = result.data[0].embedding
    return np.asarray([embedding], dtype="float32")


def _retrieve(query: str, k: int = 5) -> list[str]:
    index, metadata = _load_index()
    docs = metadata.get("docs", [])
    if not docs:
        return []
    q = _embed_query(query)
    _distances, ids = index.search(q, min(k, len(docs)))
    retrieved = []
    for doc_id in ids[0]:
        if 0 <= int(doc_id) < len(docs):
            retrieved.append(docs[int(doc_id)])
    return retrieved


def build_prompt(question: str, contexts: list[str]) -> str:
    context_block = "\n\n".join(f"Context {i + 1}:\n{ctx}" for i, ctx in enumerate(contexts))
    return (
        "You are a careful research assistant. Use only the provided context when answering. "
        "If the context is insufficient, say so briefly.\n\n"
        f"{context_block}\n\nQuestion: {question}\n\nAnswer:"
    )


@router.post("", response_model=QAResponse)
def ask_question(payload: QARequest) -> QAResponse:
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query is required.")

    contexts = _retrieve(payload.query.strip(), k=payload.k)
    if not contexts:
        raise HTTPException(status_code=503, detail="No indexed data available for retrieval.")

    prompt = build_prompt(payload.query.strip(), contexts)
    answer = call_llm(prompt, goals=[], context={"retrieved_count": len(contexts)})
    return QAResponse(answer=answer, sources=contexts)
