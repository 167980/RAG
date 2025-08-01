from fastapi import FastAPI, Depends
from app.api.ingest import router as ingest_router
from app.db.database import Base, engine
from app.api.query import router as query_router
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import DocumentChunk


app = FastAPI()
#craete tables on startup
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to the File Upload API"}


# TEMP: See all chunks
@app.get("/docs")
def read_docs(db: Session = Depends(get_db)):
    return db.query(DocumentChunk).all()


app.include_router(ingest_router, prefix="/api")
app.include_router(query_router, prefix="/api")


