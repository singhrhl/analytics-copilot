# agent/nodes.py
from agent.graph_state import AgentState, GlossaryChunk
from agent.retrieval import needs_glossary, retrieve_glossary, build_context
from agent.llm import check_ambiguity_llm, generate_clarification_question,generate_sql as generate_sql_fn

# starting node for MODE A/B Decision
def route_question(state: AgentState) -> dict:
    """Entry node — no state mutation. Exists purely as a place for the graph's
    first conditional edge to attach to (Mode A + needs_glossary -> retrieve_glossary,
    else -> check_ambiguity)."""
    return {}

# retrieval context from user input
def retrieve_glossary_node(state: AgentState) -> dict:
    chunks = retrieve_glossary(state.user_question)
    glossary_chunks = [GlossaryChunk(**c) for c in chunks]
    context = build_context(chunks)  # build_context expects the raw dict shape, unchanged
    return {
        "retrieved_glossary_chunks": glossary_chunks,
        "schema_context": context,
    }
    
# checks ambiguity in user qustion
def check_ambiguity(state: AgentState) -> dict:
    is_ambiguous = check_ambiguity_llm(state.user_question, context=state.schema_context)
    return {
        "ambiguity_status": "needs_clarification" if is_ambiguous else "clear",
    }
    
# process clerification questions response from user llm
def clarify(state: AgentState) -> dict:
    clarifying_q = generate_clarification_question(state.user_question, context=state.schema_context)
    return {
        "clarification_question": clarifying_q,
        "final_answer": clarifying_q,
        "status": "clarification_needed",
    }
    
# generate sql function when agent is sure (clerification=true)
def generate_sql_node(state: AgentState) -> dict:
    question = state.user_question
    if state.clarification_answer:
        question = f"{state.user_question}\n\nClarification: {state.clarification_answer}"

    context = state.schema_context
    if state.retry_reason:
        context += f"\n\nNOTE: A previous attempt failed for this reason: {state.retry_reason}\nPlease correct the issue and try again."

    sql = generate_sql_fn(question, context=context)
    return {"generated_sql": sql}