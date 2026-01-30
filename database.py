import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, mapped_column
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from dotenv import load_dotenv

load_dotenv()

# Configuração do Banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/modelo_ia_db")
EMBEDDING_DIM = 3584  # Dimensão do modelo qwen2.5:latest

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.now)
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user', 'assistant' or 'system'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relacionamento
    session = relationship("ChatSession", back_populates="messages")

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    source = Column(String)  # Nome do arquivo de origem
    embedding = mapped_column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.now)

def init_db():
    # Habilitar extensão vector no Postgres
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
