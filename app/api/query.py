# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from app.db.database import SessionLocal
# from app.db.models import DocumentChunk 
# from app.services.vectorizer import get_query_embedding
# from .llm_runner import ask_groq_llm
# from .llm_runner import preprocess_query_with_llm
# import json
# import numpy as np
# import re

# router = APIRouter()

# class QueryRequest(BaseModel):
#     question: str
#     top_k: int = 3  # default number of matches to return

# @router.post("/query")
# async def query_text(request: QueryRequest):
#     # S to fix spelling/phrasing
#     corrected_query = preprocess_query_with_llm(request.question)
#     keywords = ["form", "photo"]
#      # Check if query mentions metadata-only files
#     # if any(word in corrected_query.lower() for word in keywords):
#     #     # Direct metadata search
#     #     with SessionLocal() as db:
#     #         results = db.query(DocumentChunk).all()
#     #         matched = []

#     #         for row in results:
#     #             if not row.extra_metadata:
#     #                 continue
#     #             # metadata = json.loads(row.extra_metadata)


#     #             metadata = row.extra_metadata
#     #             if isinstance(metadata, str):
#     #                 try:
#     #                    metadata = json.loads(metadata)
#     #                 except Exception:
#     #                    metadata = {}  # fallback if corrupted JSON

#     #             if metadata.get("type") in ["form", "photo", "flowchart"]:
#     #                 matched.append(metadata)

#     #         # if not matched:
#     #         #     raise HTTPException(status_code=404, detail="No matching form/photo found")
#     #         if matched: 

#     #             return {
#     #                 "original_question": request.question,
#     #                 "corrected_question": corrected_query,
#     #                 "matches": matched
#     #         }


# # Tokenize query into full words
#     query_words = re.findall(r"\b\w+\b", corrected_query.lower())

# # Check for exact match of keywords
#     # if any(word in query_words for word in keywords):
#     if any(word.rstrip('s') in [w.rstrip('s') for w in query_words] for word in keywords):
#         # requested_type = next((word for word in keywords if word.rstrip('s') in [w.rstrip('s') for w in query_words]), None)

#         # question_embedding = get_query_embedding(request.question)
#         # embedding = question_embedding.flatten().tolist()
        
#     # Direct metadata search
#         with SessionLocal() as db:
#             results = db.query(DocumentChunk).all() 

#         matched = []

#         for row in results:
#             if not row.extra_metadata:
#                 continue

#             metadata = row.extra_metadata
#             if isinstance(metadata, str):
#                 try:
#                     metadata = json.loads(metadata)
#                 except Exception:
#                     metadata = {}  # fallback if corrupted JSON

#             # if metadata.get("type") in ["form", "photo", "flowchart"]:
#             # Determine which keyword triggered metadata search
           
#             requested_type = next((word for word in keywords if word.rstrip('s') in [w.rstrip('s') for w in query_words]), None)
#             if metadata.get("type") == requested_type:

#                 matched.append(metadata)

#         if matched:
#             return {
#                 "original_question": request.question,
#                 "corrected_question": corrected_query,
#                 "matches": matched
#             }

#     question_embedding = get_query_embedding(request.question)
#     embedding = question_embedding.flatten().tolist()
#     with SessionLocal() as db:
#         results = db.execute(
#             text("""
#             SELECT id, chunk_text, embedding <#> CAST(:embedding AS vector) AS distance,extra_metadata
                 
#             FROM document_chunks  
#             ORDER BY distance ASC
#             LIMIT :top_k
#             """),
#             {"embedding": embedding, "top_k": request.top_k}
#         ).fetchall()

#         if not results:
#             raise HTTPException(status_code=404, detail=question_embedding)
#     # Prepare chunks for LLM
# #         top_chunks = [f"[Page {row[3]}] {row[1]}" for row in results] # row[3] is page_number, row[1] is chunk_text
# #         # row[1] for row in results  # row[1] is chunk_text
# # #         top_chunks = [
# # #    f"(Page {meta.get('page_number', '?')}, Title: {meta.get('title', '')}, Uploader: {meta.get('uploader', '')})\n{row[1]}"
# # #    for row in results
# # #    for meta in [json.loads(row[3]) if row[3] else {}]
# # # ]

# #         # LLM call
# #         answer = ask_groq_llm(query=request.question, context_chunks=top_chunks)
# #         top_chunks = []
# #         for row in results:
# #             metadata = row[3]
# #         if isinstance(metadata, str):
# #         try:
# #             metadata = json.loads(metadata)
# #         except:
# #             metadata = {}

# #     top_chunks.append(
# #         f"(Page {metadata.get('page_number')}, Title: {metadata.get('title')}, "
# #         f"Uploader: {metadata.get('uploader')}, File Path: {metadata.get('file_path')}):\n{row[1]}"
# #     )

# # answer = ask_groq_llm(query=request.question, context_chunks=top_chunks)


# #     return {
# #     "original_question": request.question,
# #     "corrected_question": corrected_query,
# #     "matches":[
# #         {
# #             "id": row[0],
# #             "content": row[1],
# #             "score": float(row[2]),
# #             "extra_metadata":row[3]
            
# #             }
        
# #         for row in results
# #     ],
# #     "answer": answer
# # }
#         top_chunks = []
#     for row in results:
#         metadata = row[3]

#         if isinstance(metadata, str):
#             try:
#                 metadata = json.loads(metadata)
#             except:
#                 metadata = {}

#     top_chunks.append(
#         f"(Page {metadata.get('page_number')}, Title: {metadata.get('title')}, "
#         f"Uploader: {metadata.get('uploader')}, File Path: {metadata.get('file_path')}):\n{row[1]}"
#     )

#     answer = ask_groq_llm(query=request.question, context_chunks=top_chunks)

#     return {
#     "original_question": request.question,
#     "corrected_question": corrected_query,
#     "matches": [
#         {
#             "id": row[0],
#             "content": row[1],
#             "score": float(row[2]),
#             "extra_metadata": row[3]
#         }
#         for row in results
#     ],
#     "answer": answer
# }

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal
from app.db.models import DocumentChunk 
from app.services.vectorizer import get_query_embedding
from .llm_runner import ask_groq_llm
from .llm_runner import preprocess_query_with_llm
import json
import re

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3  # default number of matches to return

@router.post("/query")
async def query_text(request: QueryRequest):
    corrected_query = preprocess_query_with_llm(request.question)

    
    keywords = ["form", "photo"]

    

    # Tokenize corrected query into words
    query_words = re.findall(r"\b\w+\b", corrected_query.lower())

    # Check if query mentions metadata-only types (form, photo)
    if any(word.rstrip('s') in [w.rstrip('s') for w in query_words] for word in keywords):
        requested_type = next((word for word in keywords if word.rstrip('s') in [w.rstrip('s') for w in query_words]), None)

        question_embedding = get_query_embedding(request.question)
        embedding = question_embedding.flatten().tolist()
        
        with SessionLocal() as db:
            # Query only chunks matching requested_type, ordered by similarity
            results = db.execute( 
                text("""
                    SELECT id, chunk_text, embedding <#> CAST(:embedding AS vector) AS distance, extra_metadata
                    FROM document_chunks
                    WHERE extra_metadata->>'type' = :requested_type
                    ORDER BY distance ASC
                    LIMIT :top_k
                """),
                {"embedding": embedding, "requested_type": requested_type, "top_k": request.top_k}
            ).fetchall()

            if not results:
                raise HTTPException(status_code=404, detail="No matching photo/form found")

            seen_files = set()
            matches = []
            top_chunks = []

            for row in results:
                metadata = row[3]
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}

                file_path = metadata.get("file_path")
                file_url = metadata.get("file_url") 
                if file_path not in seen_files:
                    seen_files.add(file_path)
                    matches.append({
                        "file_path": file_path,
                        "file_url": file_url,
                        "score": float(row[2]),
                        "metadata": metadata
                    })
                    top_chunks.append(
                        f"(Page {metadata.get('page_number')}, Title: {metadata.get('title')}, "
                        f"Uploader: {metadata.get('uploader')}, File Path: {file_path}):\n{row[1]}"
                    )

        answer = ask_groq_llm(query=request.question, context_chunks=top_chunks)

        return {
            "original_question": request.question,
            "corrected_question": corrected_query,
            "matches": matches,
            "answer": {
                "text": answer,
                "metadata":matches
            }
            
        }

    # If no metadata keyword, do a general similarity search

    question_embedding = get_query_embedding(request.question)
    embedding = question_embedding.flatten().tolist()
    with SessionLocal() as db:
        results = db.execute(
            text("""
                SELECT id, chunk_text, embedding <#> CAST(:embedding AS vector) AS distance, extra_metadata
                FROM document_chunks
                ORDER BY distance ASC
                LIMIT :top_k
            """),
            {"embedding": embedding, "top_k": request.top_k}
        ).fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No matches found")

        top_chunks = []
        for row in results:
            metadata = row[3]
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            file_url = metadata.get("file_url")

            top_chunks.append(
                f"(Page {metadata.get('page_number')}, Title: {metadata.get('title')}, "
                f"Uploader: {metadata.get('uploader')}, File Path: {metadata.get('file_path')}):\n{row[1]}"
            )

    answer = ask_groq_llm(query=request.question, context_chunks=top_chunks)
    
    return {
        "original_question": request.question,
        "corrected_question": corrected_query,
        "matches": [
            {
                "id": row[0],
                "content": row[1],
                "score": float(row[2]),
                "extra_metadata": row[3]
            }
            for row in results
        ],
        "answer":{
            "answer": answer,
            "chunks": metadata
           
        }
}
