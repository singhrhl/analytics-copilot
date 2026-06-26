# agent/nodes.py
from agent.graph_state import AgentState, GlossaryChunk, MAX_RETRIES
from agent.retrieval import needs_glossary, retrieve_glossary, build_context
from agent.llm import check_ambiguity_llm, generate_clarification_question,generate_sql as generate_sql_fn
from agent.sql_guard import validate_sql_guard
from agent.db import execute_sql
from agent.validation import validate_result

# NODE: starting node for MODE A/B Decision
def route_question(state: AgentState) -> dict:
    """Entry node — no state mutation. Exists purely as a place for the graph's
    first conditional edge to attach to (Mode A + needs_glossary -> retrieve_glossary,
    else -> check_ambiguity)."""
    return {}

# EDGE: decides whether the query requires retrieval or not
def route_question_edge(state: AgentState) -> str:
    """Conditional edge from route_question. Returns the name of the next node."""
    if state.mode == "A" and needs_glossary(state.user_question):
        return "retrieve_glossary"
    return "check_ambiguity"

# NODE: retrieval context from user input
def retrieve_glossary_node(state: AgentState) -> dict:
    chunks = retrieve_glossary(state.user_question)
    glossary_chunks = [GlossaryChunk(**c) for c in chunks]
    context = build_context(chunks)  # build_context expects the raw dict shape, unchanged
    return {
        "retrieved_glossary_chunks": glossary_chunks,
        "schema_context": context,
    }
    
# NODE: checks ambiguity in user qustion
def check_ambiguity(state: AgentState) -> dict:
    is_ambiguous = check_ambiguity_llm(state.user_question, context=state.schema_context)
    return {
        "ambiguity_status": "needs_clarification" if is_ambiguous else "clear",
    }
    
# NODE: process clerification questions response from user llm
def clarify(state: AgentState) -> dict:
    clarifying_q = generate_clarification_question(state.user_question, context=state.schema_context)
    return {
        "clarification_question": clarifying_q,
        "final_answer": clarifying_q,
        "status": "clarification_needed",
    }
    
# NODE: generate sql function when agent is sure (clerification=true)
def generate_sql_node(state: AgentState) -> dict:
    question = state.user_question
    if state.clarification_answer:
        question = f"{state.user_question}\n\nClarification: {state.clarification_answer}"

    context = state.schema_context
    if state.retry_reason:
        context += f"\n\nNOTE: A previous attempt failed for this reason: {state.retry_reason}\nPlease correct the issue and try again."

    sql = generate_sql_fn(question, context=context)
    return {"generated_sql": sql}

# NODE: validates the SQL command before running
def validate_sql_guard_node(state: AgentState) -> dict:
    assert state.generated_sql is not None, "validate_sql_guard_node called before generate_sql_node — graph wiring bug."
    is_valid, guard_error = validate_sql_guard(state.generated_sql)
    if is_valid:
        return {"sql_is_valid_syntax": True}
    return {
        "sql_is_valid_syntax": False,
        "retry_reason": guard_error,
    }

# NODE: SQL executing node
def execute_sql_node(state: AgentState) -> dict:
    assert state.generated_sql is not None, "execute_sql_node called before generate_sql_node — graph wiring bug."
    result, exec_error = execute_sql(state.generated_sql)
    return {
        "execution_result": result,
        "execution_error": exec_error,
        "row_count": len(result) if result is not None else None,
    }

# NODE: validate SQL results after execution
def validate_result_node(state: AgentState) -> dict:
    is_valid, reason = validate_result(state.execution_result, state.execution_error, state.user_question)
    if is_valid:
        return {"status": "success"}
    return {"retry_reason": reason}

# EDGE: checks if edge failed or retrying
def retry_or_fail_edge(state: AgentState) -> str:
    """Conditional edge after validate_sql_guard / validate_result.
    If status is already 'success', proceed to respond.
    Otherwise, retry (incrementing retry_count) up to MAX_RETRIES, then give up."""
    if state.status == "success":
        return "respond"
    if state.retry_count >= MAX_RETRIES:
        return "fail"
    return "retry"

# EDGE : re-examin the retry-fail-endge
def guard_check_edge(state: AgentState) -> str:
    """Conditional edge after validate_sql_guard_node.
    If the guard rejected the SQL, fall through to the shared retry/fail decision.
    If it passed, proceed to execution."""
    if not state.sql_is_valid_syntax:
        return retry_or_fail_edge(state)
    return "execute_sql"

# HELPER FUNC FOR RESPOND: final output answer structure
def format_success_answer(state: AgentState) -> str:
    result = state.execution_result

    if not result:
        return "The query ran successfully but returned no rows."

    if len(result) == 1 and len(result[0]) == 1:
        value = list(result[0].values())[0]
        return f"The answer is {value}."

    if len(result) == 1:
        pairs = ", ".join(f"{k}: {v}" for k, v in result[0].items())
        return f"Result: {pairs}."

    return f"Found {len(result)} rows matching your question."

# NODE: final response
def respond(state: AgentState) -> dict:
    if state.status == "success":
        return {"final_answer": format_success_answer(state)}
    return {
        "status": "failed_after_retries",
        "final_answer": (
            f"I wasn't able to answer that after {state.retry_count} attempts. "
            f"Last issue: {state.retry_reason}"
        ),
    }