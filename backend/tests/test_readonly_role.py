import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("SUPABASE_HOST"),
    port=os.getenv("SUPABASE_PORT"),
    dbname=os.getenv("SUPABASE_DB"),
    user=os.getenv("AGENT_READONLY_USER"),
    password=os.getenv("AGENT_READONLY_PASSWORD"),
)

cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM users;")
print("Read test:", cur.fetchone())

try:
    cur.execute("DELETE FROM users WHERE user_id = 1;")
    conn.commit()
    print("WARNING: write succeeded — role is not properly read-only!")
except Exception as e:
    print("Write correctly blocked:", e)

conn.close()