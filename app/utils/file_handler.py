import os
import PyPDF2
import docx
try:
    import pytesseract
    from PIL import Image
except:
    pass

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext == ".pdf":
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif ext == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif ext in [".png", ".jpg", ".jpeg"]:
        text = pytesseract.image_to_string(Image.open(file_path))
    else:
        raise Exception("Unsupported file type")
    return text
