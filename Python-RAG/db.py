import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ragdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_tables():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding VECTOR(384)
        );"""))
        conn.commit()

def add_document(content, embedding):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO documents (content, embedding) VALUES (:content, CAST(:embedding AS vector))"),
            {"content": content, "embedding": str(embedding.tolist())}
        )
        conn.commit()

def search_similar(query_embedding, k=3):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT content FROM documents ORDER BY embedding <-> CAST(:embedding AS vector) LIMIT :k"),
            {"embedding": str(query_embedding.tolist()), "k": k}
        )
        return [row[0] for row in result]