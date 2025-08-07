from datetime import datetime
from app.services.vectorizer import get_query_embedding  
from app.db.models import DocumentChunk   
from app.db.database import SessionLocal      

def save_jobs_to_db(jobs, manual_description=None):
    db = SessionLocal()

    try:
        for job in jobs:
            # Combine title + deadline + scraped description
            chunk_text = f"{job['title']} | Deadline: {job['deadline']}\n{job['description']}"

            # Generate embedding
            embedding = get_query_embedding(chunk_text)
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()
            if isinstance(embedding, list) and any(isinstance(i, list) for i in embedding):
                embedding = [item for sublist in embedding for item in sublist]

            # Metadata (manual description stored separately)
            extra_metadata = {
                "uploader": "system_scraper",
                "uploaded_time": datetime.utcnow().isoformat(),
                "file_type": "job_vacancy",
                "file_path": "web_scrape",
                "url": job["url"],
                "manual_description": manual_description
            }

            doc = DocumentChunk(
                filename="worldlink_jobs",
                chunk_text=chunk_text,
                embedding=embedding,
                extra_metadata=extra_metadata
            )

            db.add(doc)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
