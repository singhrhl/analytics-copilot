# agent/llm.py
import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

SCHEMA_CONTEXT = """
Table: users
  user_id          INTEGER, primary key
  signup_date       DATE
  grade             SMALLINT (values 6-12)
  device            TEXT (values: android, ios, web)
  curriculum        TEXT (values: CBSE, ICSE, JEE, NEET, State Board)
  target_exam       TEXT (values: JEE, NEET, Boards, undeclared)
  is_test_account   BOOLEAN

Table: sessions
  session_id           INTEGER, primary key
  user_id               INTEGER, foreign key -> users.user_id
  start_time            TIMESTAMP
  duration_minutes      NUMERIC
  session_goal          TEXT (values: deep_study, revision, quick_quiz)
  is_duration_mismatch  BOOLEAN

Table: events
  event_id     INTEGER, primary key
  session_id    INTEGER, foreign key -> sessions.session_id
  event_type    TEXT (values: lesson_started, lesson_completed, quiz_submitted, video_completed, doubt_raised)
  timestamp     TIMESTAMP
"""

SQL_GEN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a SQL generation assistant for a Postgres database.
Given the schema below and additional context, write a single SELECT query
(CTEs with WITH...SELECT are allowed) that answers the user's question.
Return ONLY the raw SQL, no markdown formatting, no explanation, no backticks.

Schema:
{schema}

Additional context (if any):
{context}
"""),
    ("human", "{question}"),
])

MAX_LLM_RETRIES = 3

def generate_sql(question: str, context: str = "") -> str:
    chain = SQL_GEN_PROMPT | llm

    last_error = None
    for attempt in range(MAX_LLM_RETRIES):
        try:
            response = chain.invoke({"schema": SCHEMA_CONTEXT, "context": context, "question": question})
            content = response.content
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            sql = content.strip()
            sql = re.sub(r"^```sql\s*|^```\s*|```$", "", sql, flags=re.MULTILINE).strip()
            return sql
        except Exception as e:
            last_error = e
            if attempt < MAX_LLM_RETRIES - 1:
                import time
                wait = 2 ** attempt
                print(f"Gemini call failed (attempt {attempt+1}/{MAX_LLM_RETRIES}): {e}. Retrying in {wait}s...")
                time.sleep(wait)

    raise RuntimeError(f"Gemini API failed after {MAX_LLM_RETRIES} attempts: {last_error}")