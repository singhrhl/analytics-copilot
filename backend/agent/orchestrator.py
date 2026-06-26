# agent/orchestrator.py
from agent.llm import generate_sql
from agent.sql_guard import validate_sql_guard
from agent.db import execute_sql
from agent.validation import validate_result
from agent.retrieval import needs_glossary, retrieve_glossary, build_context

MAX_RETRIES = 2

def run_query_with_retry(question: str) -> dict:
    context = ""
    if needs_glossary(question):
        chunks = retrieve_glossary(question)
        context = build_context(chunks)

    retry_count = 0
    retry_reason = None
    sql = None

    while retry_count <= MAX_RETRIES:
        attempt_context = context
        if retry_reason:
            attempt_context += f"\n\nNOTE: A previous attempt failed for this reason: {retry_reason}\nPlease correct the issue and try again."

        sql = generate_sql(question, context=attempt_context)

        is_valid, guard_error = validate_sql_guard(sql)
        if not is_valid:
            retry_reason = guard_error
            retry_count += 1
            continue

        result, exec_error = execute_sql(sql)
        result_valid, result_reason = validate_result(result, exec_error, question)

        if result_valid:
            return {
                "status": "success",
                "sql": sql,
                "result": result,
                "retry_count": retry_count,
            }

        retry_reason = result_reason
        retry_count += 1

    return {
        "status": "failed_after_retries",
        "sql": sql,
        "result": None,
        "retry_count": retry_count,
        "last_reason": retry_reason,
    }