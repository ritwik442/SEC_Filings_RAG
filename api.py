from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag import answer_question
from vectorstore import VectorStore
import os

load_dotenv()

app = FastAPI(
    title="SEC Filings RAG",
    description="Ask grounded questions about SEC filings. Answers come with sources.",
    version="0.1.0",
)

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    store = VectorStore.load()
    print(f"Loaded store with {len(store)} chunks")
except FileNotFoundError:
    store = None
    print("No store found. Run `python ingest.py` to build the index.")



class AskRequest(BaseModel):
    """What a client must send. Field validators reject bad input automatically."""
    question: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(6, ge=1, le=20)              
    company: Optional[str] = None                


class Source(BaseModel):
    """One retrieved chunk, with provenance and a preview for the frontend."""
    company: str
    filing_type: str
    chunk_index: int
    score: float
    preview: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]



@app.get("/health")
def health():
    """Liveness + readiness check. Lets the frontend show 'Indexing...' if not ready."""
    return {
        "status": "ok",
        "chunks_indexed": len(store) if store else 0,
        "ready": store is not None,
    }

@app.get("/companies")
def companies():
    """List companies currently in the index, with their filing types."""
    if store is None:
        return {"companies": []}
    seen = {}
    for r in store.records:
        seen.setdefault(r["company"], set()).add(r["filing_type"])
    return {"companies": [
        {"ticker": c, "filings": sorted(types)} for c, types in seen.items()
    ]}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """The main RAG endpoint. Retrieves and generates a grounded answer."""
    if store is None:

        raise HTTPException(status_code=503, detail="Index not built. Run ingest.py first.")

    answer, hits = answer_question(req.question, store, k=req.k, company=req.company)

    return AskResponse(
        question=req.question,
        answer=answer,
        sources=[
            Source(
                company=r["company"],
                filing_type=r["filing_type"],
                chunk_index=r["chunk_index"],
                score=round(s, 3),

                preview=r["text"][:200] + ("..." if len(r["text"]) > 200 else ""),
            )
            for r, s in hits
        ],
    )