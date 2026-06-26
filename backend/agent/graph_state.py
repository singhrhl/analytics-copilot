# agent/graph_state.py
from typing import Literal
from pydantic import BaseModel, Field, model_validator

MAX_RETRIES = 2  # single source of truth; orchestrator.py currently hardcodes this separately — worth unifying later


class GlossaryChunk(BaseModel):
    id: str
    title: str
    content: str
    similarity: float = Field(ge=-1.0, le=1.0)


class AgentState(BaseModel):
    user_question: str
    mode: Literal["A", "B"]
    conversation_history: list[dict] = Field(default_factory=list)

    schema_context: str = ""
    retrieved_glossary_chunks: list[GlossaryChunk] = Field(default_factory=list)  # Mode A only; [] for Mode B

    ambiguity_status: Literal["clear", "needs_clarification"] = "clear"
    clarification_question: str | None = None
    clarification_answer: str | None = None

    generated_sql: str | None = None
    sql_is_valid_syntax: bool = False

    execution_result: list[dict] | None = None
    execution_error: str | None = None
    row_count: int | None = None

    retry_count: int = Field(default=0, ge=0, le=MAX_RETRIES)
    retry_reason: str | None = None

    final_answer: str | None = None
    status: Literal["success", "clarification_needed", "failed_after_retries"] | None = None

    @model_validator(mode="after")
    def clarification_answer_requires_pending_question(self) -> "AgentState":
        if self.clarification_answer is not None and self.clarification_question is None:
            raise ValueError(
                "clarification_answer set without a prior clarification_question — "
                "this shouldn't happen given the graph's edges, so if it does, "
                "something upstream merged state incorrectly."
            )
        return self