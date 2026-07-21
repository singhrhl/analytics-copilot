import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from langgraph.types import Command

from agent.graph import build_graph
from agent.graph_state import AgentState

from decimal import Decimal

def serialize_result(data: list[dict] | None) -> list[dict] | None:
    """Convert Decimal values in execution_result to float for JSON serialization."""
    if not data:
        return data
    return [
        {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}
        for row in data
    ]

app = FastAPI(title="Analytics Copilot API")

# ── Compiled graph (built once at startup) ───────────────
graph = build_graph()

# ── Request/response models ──────────────────────────────
class QueryRequest(BaseModel):
    question: str
    mode: Literal['A','B'] = 'A'

class ClarifyRequest(BaseModel):
    answer: str
    thread_id: str

class ClarificationResponse(BaseModel):
    type: str = "clarification"
    question: str
    thread_id: str

class AnswerResponse(BaseModel):
    type: str = "answer"
    answer: str
    data: list[dict] | None
    thread_id: str

# ── Endpoints ────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query(req: QueryRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = graph.invoke(
            AgentState(user_question=req.question, mode=req.mode),
            config=config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if "__interrupt__" in result:
        return ClarificationResponse(
            question=result["__interrupt__"][0].value,
            thread_id=thread_id,
        )

    return AnswerResponse(
        answer=result.get("final_answer", "No answer returned."),
        data=serialize_result(result.get("execution_result")),
        thread_id=thread_id,
    )

@app.post("/clarify")
def clarify(req: ClarifyRequest):
    config = {"configurable": {"thread_id": req.thread_id}}

    try:
        result = graph.invoke(Command(resume=req.answer), config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AnswerResponse(
        answer=result.get("final_answer", "No answer returned."),
        data=serialize_result(result.get("execution_result")),
        thread_id=req.thread_id,
    )