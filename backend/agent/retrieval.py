# agent/retrieval.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from agent.db import get_readonly_connection

embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

GLOSSARY_KEYWORDS = {
    "dau": ["dau", "daily active"],
    "mau": ["mau", "monthly active"],
    "retention": ["retention", "retain"],
    "session_goal": ["session goal", "deep study", "revision", "quick quiz", "session type"],
    "target_exam": ["target exam", "exam target", "jee student", "neet student", "prepping for"],
}

def needs_glossary(question: str) -> bool:
    q_lower = question.lower()
    for keywords in GLOSSARY_KEYWORDS.values():
        if any(kw in q_lower for kw in keywords):
            return True
    return False

def retrieve_glossary(question: str, top_k: int = 2) -> list[dict]:
    query_embedding = embeddings_model.embed_query(question)

    conn = get_readonly_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, content, 1 - (embedding <=> %s::extensions.vector) AS similarity
        FROM glossary
        ORDER BY embedding <=> %s::extensions.vector
        LIMIT %s;
        """,
        (query_embedding, query_embedding, top_k),
    )
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "content": r[2], "similarity": r[3]} for r in rows]

def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    return "\n\n".join(f"[{c['title']}]\n{c['content']}" for c in chunks)