# test_retrieval.py
import os
import psycopg2
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

conn = psycopg2.connect(
    host=os.getenv("SUPABASE_HOST"),
    port=os.getenv("SUPABASE_PORT"),
    dbname=os.getenv("SUPABASE_DB"),
    user=os.getenv("AGENT_READONLY_USER"),
    password=os.getenv("AGENT_READONLY_PASSWORD"),
)
cur = conn.cursor()

TEST_QUESTIONS = [
    "What's our DAU?",
    "How many users are active monthly?",
    "What's our retention?",
    "How long are deep study sessions supposed to be?",
    "Which exam are students preparing for?",
]

for question in TEST_QUESTIONS:
    query_embedding = embeddings_model.embed_query(question)

    cur.execute(
        """
        SELECT id, title, 1 - (embedding <=> %s::extensions.vector) AS similarity
        FROM glossary
        ORDER BY embedding <=> %s::extensions.vector
        LIMIT 3;
        """,
        (query_embedding, query_embedding),
    )
    results = cur.fetchall()

    print(f"\nQuestion: {question}")
    for id_, title, similarity in results:
        print(f"  {id_:15s} ({title:30s}) similarity={similarity:.4f}")

conn.close()