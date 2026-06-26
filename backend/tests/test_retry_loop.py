# tests/test_retry_loop.py
import agent.llm as llm_module
from agent.orchestrator import run_query_with_retry

call_log = []

def fake_generate_sql(question, context=""):
    call_log.append(context)
    attempt = len(call_log)
    if attempt == 1:
        return "DELETE FROM users"
    elif attempt == 2:
        return "SELECT * FROM users WHERE signup_date = '1900-01-01'"
    else:
        return "SELECT count(*) FROM users"

real_generate_sql = llm_module.generate_sql
llm_module.generate_sql = fake_generate_sql

# orchestrator imported generate_sql directly, so patch it there too
import agent.orchestrator as orch_module
orch_module.generate_sql = fake_generate_sql

outcome = run_query_with_retry("How many users do we have?")
print(f"Final outcome: {outcome}")

orch_module.generate_sql = real_generate_sql