import os
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from pathlib import Path
import easyocr
import pandas as pd
import fitz  
import cv2
import camelot
from app.services.vectorizer import save_chunks_to_db
from docx import Document
from datetime import datetime
from app.db.models import DocumentChunk
from app.db.database import SessionLocal
from app.services.vectorizer import embedder
from app.services.vectorizer import chunk_text

router = APIRouter()

# constants
UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

# Separate folders
FORM_DIR = UPLOAD_DIR / "forms"
FORM_DIR.mkdir(exist_ok=True)

PHOTO_DIR = UPLOAD_DIR / "photos"
PHOTO_DIR.mkdir(exist_ok=True)


def save_file_metadata_to_db(filename: str, uploaded_by: str, title: str, file_path: str, file_type: str, description=None):
    db = SessionLocal()
    try:
          # Generate the file_url
        base_url = "http://localhost:8000/media"  # Replace with your actual domain or env var
        print(f"Base URL: {base_url}")
        print(f"File path: {file_path}")
        relative_path = file_path.replace("uploaded_files\\", "").replace("\\", "/")
        print(f"Relative path: {relative_path}")
        file_url = f"{base_url}/{relative_path}"


        metadata = {
            "uploader": uploaded_by,
            "title": title,
            "page_number": 1,
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_path": file_path,
            "file_url": file_url,
            "type": file_type,
            "description":description
        }
        if description:  # Only chunk/embed description if provided
            chunks = chunk_text(description)       # Reuse your chunking logic
            vectors = embedder.encode(chunks)      # Generate embeddings

            for chunk, vec in zip(chunks, vectors):
                new_entry = DocumentChunk(
                    filename=filename,
                    chunk_text=chunk,              # store chunked description
                    embedding=vec,                 # store embedding
                    extra_metadata=metadata        # keep metadata JSON
                )
                db.add(new_entry)

        else:  # No description → Save only metadata
            new_entry = DocumentChunk(
                filename=filename,
                chunk_text=None,
                embedding=None,
                extra_metadata=metadata
            )
        db.add(new_entry)
        db.commit()
    finally:
        db.close()

@router.post("/upload_form")
async def upload_form(
    files: List[UploadFile] = File(...),
    uploaded_by: str = Form(...),
    title: str = Form(...),
    description: str = Form(...)
):
    extracted_results = []
    for file in files:
        save_path = FORM_DIR / file.filename

        # Save file
        with open(save_path, "wb") as buffer:
            buffer.write(await file.read())

        # Save metadata to DB
        save_file_metadata_to_db(file.filename, uploaded_by, title, str(save_path), "form", description)

        extracted_results.append({
            "filename": file.filename,
            "uploader": uploaded_by,
            "title": title,
            "file_path": str(save_path),
            "description":description,
            "type": "form"
            
        })

    return {"status": "success", "files": extracted_results}

@router.post("/upload_photo")
async def upload_photo(
    files: List[UploadFile] = File(...),
    uploaded_by: str = Form(...),
    title: str = Form(...),
    description: str=Form(...)
):
    allowed_exts = {"png", "jpg", "jpeg"}
    extracted_results = []
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        if ext not in allowed_exts:
            raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.filename}")

        save_path = PHOTO_DIR / file.filename

        # Save file
        with open(save_path, "wb") as buffer:
            buffer.write(await file.read())

        # Save metadata to DB
        save_file_metadata_to_db(file.filename, uploaded_by, title, str(save_path), "photo",description)

        extracted_results.append({
            "filename": file.filename,
            "uploader": uploaded_by,
            "title": title,
            "file_path": str(save_path),
            "type": "photo",
            "description":description
        })

    return {"status": "success", "files": extracted_results}

reader = easyocr.Reader(['en'], gpu=False)  # OCR reader

# route to upload and extract text from files
@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...), 
    uploaded_by: str = Form(...),
    title: str = Form(...),
    
):
    extracted_results = []

    for file in files:
        ext = file.filename.split(".")[-1].lower()
        save_path = UPLOAD_DIR / file.filename

        if ext not in ["pdf", "txt", "csv", "png", "jpg", "jpeg","doc","docx"]:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        # Save file
        with open(save_path, "wb") as buffer:
            buffer.write(await file.read())

        # Extract and structure text per page and chunk
        doc_text = ""
        if ext == "pdf":
            pages = extract_text_from_pdf(save_path)
        else:
            # Wrap non-pdf as single "page" with page_number = 1
            pages = [{"page_number": 1, "text": extract_text_by_filetype(save_path, ext)}]

        for page in pages:
            page_number = page["page_number"]
            page_text = page["text"]
            print(page_text)
            doc_text += page_text + "\n"
            chunks = page_text.split("\n\n")
  

            for chunk in chunks:
                if chunk.strip():
                    save_chunks_to_db(chunk.strip(), file.filename, uploaded_by, title, page_number)


        extracted_results.append({
            "filename": file.filename,
            "uploader": uploaded_by,
            "title": title,
            "doc": doc_text,
            "text": page_text[:5]  # Preview first few chunks
        })

    return {"status": "success", "files": extracted_results}


# FILE HANDLER FUNCTIONS 

def extract_text_by_filetype(filepath: Path, filetype: str) -> str:
    filetype = filetype.lower()
    
    if filetype == "pdf":
        return extract_text_from_pdf(filepath)
    elif filetype in ["doc","docx"]:
        return extract_text_from_docx(filepath)
    elif filetype == "txt":
        return extract_text_from_txt(filepath)
    elif filetype == "csv":
        return extract_text_from_csv(filepath)
    elif filetype in ["jpg", "jpeg", "png"]:
        return extract_text_from_image(filepath)

    else:
        return "[Unsupported filetype for text extraction]"

def extract_text_from_pdf(filepath: Path) -> List[dict]:
    pages = []
    with fitz.open(filepath) as doc:
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            page_text = re.sub(r"^Page\s*\d+\s*", "", text, flags = re.IGNORECASE)  # Remove "Page X" headers
            pages.append({
                "page_number": i + 1,
                "text": page_text
            })
         # 2. Extract tables using Camelot (Markdown format)
    
    try:

        tables = camelot.read_pdf(str(filepath), pages='all')
        for table in tables:
            df = table.df
            page_num = int(table.page)

            # For each column, create one chunk with header + all values
            for col in df.columns:
                # Collect all values in this column including header
                col_values = [col] + df[col].tolist()
                # Join with newlines to form chunk text
                chunk_text = "\n".join(str(v) for v in col_values if str(v).strip())
                pages.append({
                    "page_number": page_num,
                    "text": chunk_text
                })

    except Exception as e:
        print(f"Table extraction error: {e}")

    return pages

def extract_text_from_docx(filepath: Path) -> str:
    doc = Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text).strip()
     
    

def extract_text_from_txt(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_text_from_csv(filepath: Path) -> str:
    """
    Minimal CSV handler: convert to descriptive sentences row-wise.
    Compatible with existing upload logic (returns single string).
    """
    try:
        df = pd.read_csv(filepath)

        rows_text = []
        for idx, row in df.iterrows():
            # Generate descriptive sentences per row
            row_text = "; ".join([f"{col}: {row[col]}" for col in df.columns]) + "."
            rows_text.append(row_text)

        return "\n".join(rows_text)  # Single string, rows separated by newline

    except Exception as e:
        print(f"CSV extraction error: {e}")
        return ""


def extract_text_from_image(filepath: Path) -> List[dict]:
  
    # Extract text from an image using OCR and return column-wise chunks.
    # Page number is always 1 for images.
    
    pages = []
    try:
        # OCR extraction
        image = cv2.imread(str(filepath))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        result = reader.readtext(gray, detail=0)  # List of text segments

        # Join OCR results into raw text
        raw_text = " ".join(result).strip()

        # Heuristic: split by newlines or large spaces to separate rows
        rows = raw_text.split("\n")

        # Convert rows to columns (assume words per row are space separated)
        split_rows = [row.split() for row in rows if row.strip()]

        pages.append({
                "page_number": 1,
                "text": raw_text
            })

    except Exception as e:
        print(f"Image OCR extraction error: {e}")

    return raw_text