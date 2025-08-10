from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
from .database import Base

Base=declarative_base()

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    chunk_text = Column(String)
    embedding = Column(Vector(384))  # Assuming 384-dim model like 'all-MiniLM-L6-v2'
    extra_metadata= Column(JSONB)