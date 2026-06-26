# agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from agent.graph_state import AgentState
from agent.nodes import (
    route_question,
    route_question_edge,
    retrieve_glossary_node,
    check_ambiguity,
    clarify,
    generate_sql_node,
    validate_sql_guard_node,
    guard_check_edge,
    execute_sql_node,
    validate_result_node,
    retry_or_fail_edge,
    respond,
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("route_question", route_question)
    graph.add_node("retrieve_glossary", retrieve_glossary_node)
    graph.add_node("check_ambiguity", check_ambiguity)
    graph.add_node("clarify", clarify)
    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("validate_sql_guard", validate_sql_guard_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("validate_result", validate_result_node)
    graph.add_node("respond", respond)

    graph.set_entry_point("route_question")

    graph.add_conditional_edges(
        "route_question",
        route_question_edge,
        {
            "retrieve_glossary": "retrieve_glossary",
            "check_ambiguity": "check_ambiguity",
        },
    )

    graph.add_edge("retrieve_glossary", "check_ambiguity")

    graph.add_conditional_edges(
        "check_ambiguity",
        lambda state: "clarify" if state.ambiguity_status == "needs_clarification" else "generate_sql",
        {
            "clarify": "clarify",
            "generate_sql": "generate_sql",
        },
    )

    graph.add_edge("clarify", "generate_sql")

    graph.add_edge("generate_sql", "validate_sql_guard")

    graph.add_conditional_edges(
        "validate_sql_guard",
        guard_check_edge,
        {
            "execute_sql": "execute_sql",
            "retry": "generate_sql",
            "fail": "respond",
        },
    )

    graph.add_edge("execute_sql", "validate_result")

    graph.add_conditional_edges(
        "validate_result",
        retry_or_fail_edge,
        {
            "respond": "respond",
            "retry": "generate_sql",
            "fail": "respond",
        },
    )

    graph.add_edge("respond", END)

    serde = JsonPlusSerializer(allowed_msgpack_modules=[("agent.graph_state", "GlossaryChunk")])
    checkpointer = MemorySaver(serde=serde)
    return graph.compile(checkpointer=checkpointer)