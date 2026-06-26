# agent/validation.py

AGGREGATE_HINTS = ["how many", "count", "average", "total", "what is the", "what was the"]

def validate_result(result: list[dict] | None, exec_error: str | None, question: str) -> tuple[bool, str]:
    """Returns (is_valid, reason). is_valid=False triggers retry."""
    if exec_error:
        return False, f"Execution error: {exec_error}"

    if result is None:
        return False, "No result returned (unexpected null result with no error)."

    if len(result) == 0:
        return False, "Query returned zero rows."

    looks_like_single_value_question = any(hint in question.lower() for hint in AGGREGATE_HINTS)

    if looks_like_single_value_question and len(result) > 1:
        return False, f"Expected a single aggregate value but got {len(result)} rows."

    return True, ""