# from sqlalchemy import Column, String, Text, DateTime
# from app.db.database import Base
# from datetime import datetime

# class Document(Base):
#     __tablename__ = "documents"

#     id = Column(String, primary_key=True, index=True)  # text hash
#     filename = Column(String, nullable=False)
#     uploaded_by = Column(String, nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     content = Column(Text, nullable=False)

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB,BYTEA
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
    # uploader = Column(String)
    # uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    # title = Column(String)
    # page_number = Column(Integer)  # Store page number as string for flexibility
    extra_metadata= Column(JSONB)