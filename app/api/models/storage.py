# from app.db.database import SessionLocal
# from app.db.models import Document

# def save_document_to_db(doc_data: dict) -> bool:
#     session = SessionLocal()
#     try:
#         exists = session.query(Document).filter_by(id=doc_data["id"]).first()
#         if exists:
#             return False  # Duplicate
#         doc = Document(
#             id=doc_data["id"],
#             filename=doc_data["filename"],
#             uploaded_by=doc_data["uploaded_by"],
#             timestamp=doc_data["timestamp"],
#             content=doc_data["content"]
#         )
#         session.add(doc)
#         session.commit()
#         return True
#     finally:
#         session.close()
