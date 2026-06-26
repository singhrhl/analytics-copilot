# agent/sql_guard.py
import re

WRITE_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

def validate_sql_guard(sql: str) -> tuple[bool, str]:
    stripped = sql.strip()
    starts_ok = bool(re.match(r"^\s*(SELECT|WITH)\b", stripped, re.IGNORECASE))
    if not starts_ok:
        return False, "Query must start with SELECT or WITH."
    if WRITE_KEYWORDS.search(stripped):
        return False, "Query contains a disallowed write/DDL keyword."
    return True, ""