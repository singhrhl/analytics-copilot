# agent/llm.py
import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Schema Context for the llm
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
  
  Note on data recency: This dataset contains session and event data for the
period 2025-01-01 through 2025-12-28 only. There is no more recent data.
When a question asks for a metric "today," "currently," or without specifying
a date (e.g. "what's our DAU?"), interpret it as asking for the most recent
calendar day that has data — compute this via SQL (e.g. using MAX(start_time)
or a subquery), do not assume the literal current date.
"""

# prompt to generate SQL
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

# Extracting text from response
def extract_text(response) -> str:
    """Gemini/LangChain sometimes returns response.content as a list of content-part
    dicts instead of a flat string. Normalizes either shape to plain text."""
    content = response.content
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return content

# SQL generation
def generate_sql(question: str, context: str = "") -> str:
    chain = SQL_GEN_PROMPT | llm

    last_error = None
    for attempt in range(MAX_LLM_RETRIES):
        try:
            response = chain.invoke({"schema": SCHEMA_CONTEXT, "context": context, "question": question})
            content = response.content
            sql = extract_text(response).strip()
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

# Checking Ambiguity
AMBIGUITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are checking whether a user's analytics question is clear enough
to generate SQL for, or genuinely ambiguous given the context below.

A question is ambiguous ONLY if the context explicitly warns that the term has multiple
competing definitions and instructs you to ask for clarification. Do not invent ambiguity
that isn't called out in the context — most questions are clear.

Context (if any):
{context}

Respond with EXACTLY one word: "clear" or "ambiguous". Nothing else."""),
    ("human", "{question}"),
])

def check_ambiguity_llm(question: str, context: str = "") -> bool:
    """Returns True if ambiguous, False if clear."""
    chain = AMBIGUITY_PROMPT | llm
    response = chain.invoke({"question": question, "context": context})
    return extract_text(response).strip().lower().startswith("ambig")

# Clerification on user prompt if prompt flagged as ambiguous
CLARIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """The user's question was flagged as ambiguous based on the context below,
which explains what's ambiguous about it. Write a short, direct clarifying question asking
the user to specify which definition/option they mean. Do not explain why it's ambiguous —
just ask the question naturally, the way a helpful analyst would.

Context:
{context}"""),
    ("human", "{question}"),
])

def generate_clarification_question(question: str, context: str = "") -> str: 
    chain = CLARIFICATION_PROMPT | llm
    response = chain.invoke({"question": question, "context": context})
    return extract_text(response).strip()