# embed_glossary.py
import os
import psycopg2
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

GLOSSARY_ENTRIES = [
    {
        "id": "dau",
        "title": "Daily Active Users (DAU)",
        "text": "Daily Active Users (DAU): The count of distinct user_ids with at least one row in sessions where start_time falls on the given calendar day. Test accounts (users.is_test_account = True) must be excluded from this count — they are used for internal QA and do not represent real usage. DAU is calculated per calendar day in IST, not UTC."
    },
    {
        "id": "mau",
        "title": "Monthly Active Users (MAU)",
        "text": "Monthly Active Users (MAU): The count of distinct user_ids with at least one row in sessions where start_time falls within the given calendar month. Same test-account exclusion rule as DAU applies. Note: MAU is not simply 'average of daily DAU' — it is a distinct-user count over the full month window, so it will typically be smaller than the sum of daily DAU values for that month."
    },
    {
        "id": "retention",
        "title": "Retention",
        "text": "Retention: There are three retention metrics tracked internally, and 'retention' alone is ambiguous without specifying which: D1 Retention is the percent of users who had a session on signup day who also had a session exactly 1 day later. D7 Retention is the percent of users who had a session on signup day who also had at least one session in days 2-7 after signup. Curriculum Retention is the percent of users still having at least one session in a given month, among users who signed up under the same curriculum 3+ months prior — used by the curriculum team, not the growth team. If a query asks about 'retention' without specifying which type, ask the user to clarify before proceeding — these three metrics can differ by 15-20 percentage points and silently picking one produces a misleading answer."
    },
    {
        "id": "session_goal",
        "title": "Session Goal Categories",
        "text": "Session Goal Categories: Sessions are tagged by the student at start with an intended goal: deep_study (typically 60-120 min, focused single-topic study), revision (typically 30-60 min, reviewing previously covered material), quick_quiz (typically 15-30 min, self-testing). These are student-declared intentions, not enforced durations — actual session length can deviate from the typical range."
    },
    {
        "id": "target_exam",
        "title": "Target Exam Categories",
        "text": "Target Exam Categories: target_exam reflects the exam a student is preparing for, declared once at signup (JEE, NEET, Boards, or undeclared). undeclared means the student has not declared a specific competitive/board exam target — typically general practice or younger students not yet in an exam-prep phase. When a question asks about a specific exam's users (e.g., 'JEE students'), filter on the exact target_exam value — do not include undeclared rows, and do not assume Boards overlaps with JEE/NEET even though some students may prepare for both in reality; the dataset only stores one declared target per student."
    },
]

conn = psycopg2.connect(
    host=os.getenv("SUPABASE_HOST"),
    port=os.getenv("SUPABASE_PORT"),
    dbname=os.getenv("SUPABASE_DB"),
    user="postgres",
    password=os.getenv("SUPABASE_ADMIN_PASSWORD"),
)
cur = conn.cursor()

for entry in GLOSSARY_ENTRIES:
    embedding = embeddings_model.embed_documents([entry["text"]])[0]
    cur.execute(
        """
        INSERT INTO glossary (id, title, content, embedding)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET title = EXCLUDED.title, content = EXCLUDED.content, embedding = EXCLUDED.embedding;
        """,
        (entry["id"], entry["title"], entry["text"], embedding),
    )
    print(f"Inserted/updated: {entry['id']}")

conn.commit()
conn.close()
print("Done.")