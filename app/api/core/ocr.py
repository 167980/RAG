# import easyocr
# from pdf2image import convert_from_path
# import uuid
# import os

# reader = easyocr.Reader(['en'])

# def extract_text_from_pdf(pdf_path: str) -> str:
#     images = convert_from_path(pdf_path)
#     text = ""
#     for img in images:
#         temp_path = f"temp_{uuid.uuid4().hex}.png"
#         img.save(temp_path)
#         lines = reader.readtext(temp_path, detail=0, paragraph=True)
#         text += "\n".join(lines) + "\n"
#         os.remove(temp_path)
#     return text.strip()

# def extract_text_from_image(image_path: str) -> str:
#     lines = reader.readtext(image_path, detail=0, paragraph=True)
#     return "\n".join(lines).strip()
