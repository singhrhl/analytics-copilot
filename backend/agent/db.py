# agent/db.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_readonly_connection():
    return psycopg2.connect(
        host=os.getenv("SUPABASE_HOST"),
        port=os.getenv("SUPABASE_PORT"),
        dbname=os.getenv("SUPABASE_DB"),
        user=os.getenv("AGENT_READONLY_USER"),
        password=os.getenv("AGENT_READONLY_PASSWORD"),
    )

def execute_sql(sql: str) -> tuple[list[dict] | None, str | None]:
    try:
        conn = get_readonly_connection()
        cur = conn.cursor()
        cur.execute(sql)
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        result = [dict(zip(colnames, row)) for row in rows]
        conn.close()
        return result, None
    except Exception as e:
        return None, str(e)