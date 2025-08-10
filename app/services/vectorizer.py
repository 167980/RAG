from sentence_transformers import SentenceTransformer
from app.db.database import SessionLocal
from app.db.models import DocumentChunk
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime, timedelta, timezone

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,      # Size of each chunk
        chunk_overlap=100,    # Overlap between chunks
        length_function=len,
    )
    return text_splitter.split_text(text)

def get_query_embedding(text):
    chunks = chunk_text(text)
    vectors = embedder.encode(chunks)
    return vectors

def save_chunks_to_db(text: str, filename: str, uploader: str = "anonymous", title: str = "", page_number: int = 0,file_path: str=""):

    chunks = chunk_text(text)
    vectors = embedder.encode(chunks)

    session = SessionLocal()
    try:
        for chunk, vec in zip(chunks, vectors):
            
            nepal_tz = timezone(timedelta(hours=5, minutes=45))

            uploaded_time = datetime.now(nepal_tz)

            file_path = f"/media/uploaded_files/{filename}"

            metadata={
                "uploader":uploader,
                "title":title,
                "page_number":int(page_number),
                "uploaded_at": datetime.utcnow().isoformat() ,
                "file_path":file_path 
            }
            record = DocumentChunk(
                filename=filename,
                chunk_text=chunk,
                embedding=vec.tolist(),
                extra_metadata=metadata
               
            )
            session.add(record)
        session.commit()
    finally:
        session.close()
    
