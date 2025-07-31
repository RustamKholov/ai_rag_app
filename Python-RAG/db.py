import os
from sqlalchemy import create_engine, text, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional, Generator
import numpy as np

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Document(Base):
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False, index=True)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Document(id={self.id}, content='{self.content[:50]}...', created_at={self.created_at})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:

    return SessionLocal()

def create_tables():
    
    Base.metadata.create_all(bind=engine)


def add_document(content: str, embedding: np.ndarray) -> Document:

    db = get_db_session()
    try:
        
        embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        
        document = Document(
            content=content,
            embedding=embedding_list
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def search_similar(query_embedding: np.ndarray, k: int = 3) -> List[Document]:
    db = get_db_session()
    try:
        embedding_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
        
        documents = db.query(Document)\
            .order_by(Document.embedding.cosine_distance(embedding_list))\
            .limit(k)\
            .all()
        return documents
    finally:
        db.close()

def get_document_by_id(document_id: int) -> Optional[Document]:
    db = get_db_session()
    try:
        return db.query(Document).filter(Document.id == document_id).first()
    finally:
        db.close()

def get_all_documents(skip: int = 0, limit: int = 100) -> List[Document]:
    db = get_db_session()
    try:
        return db.query(Document)\
            .order_by(Document.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    finally:
        db.close()

def update_document(document_id: int, content: str = None, embedding: np.ndarray = None) -> Optional[Document]:
    db = get_db_session()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        
        if content is not None:
            document.content = content
        
        if embedding is not None:
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            document.embedding = embedding_list
        
        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_document(document_id: int) -> bool:
    db = get_db_session()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        db.delete(document)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_documents_count() -> int:
    db = get_db_session()
    try:
        return db.query(Document).count()
    finally:
        db.close()

def search_documents_by_content(search_term: str, limit: int = 10) -> List[Document]:
    db = get_db_session()
    try:
        return db.query(Document)\
            .filter(Document.content.ilike(f"%{search_term}%"))\
            .order_by(Document.created_at.desc())\
            .limit(limit)\
            .all()
    finally:
        db.close()
        