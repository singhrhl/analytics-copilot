# tests/test_sql_guard.py
from agent.sql_guard import validate_sql_guard

test_cases = [
    "DELETE FROM users WHERE user_id = 1",
    "SELECT * FROM users; DROP TABLE users;",
    "UPDATE users SET grade = 12",
    "WITH active AS (SELECT * FROM users) SELECT COUNT(*) FROM active",
    "  select count(*) from users",
]

for tc in test_cases:
    valid, err = validate_sql_guard(tc)
    print(f"  [{'PASS' if valid else 'BLOCKED'}] {tc[:60]!r} -> {err}")