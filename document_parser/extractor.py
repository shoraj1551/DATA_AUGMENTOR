import io
import pypdf
import docx
import pptx
import openpyxl
import pandas as pd
from PIL import Image
import pytesseract

def extract_text_from_file(uploaded_file):
    """
    Unified extractor for various file types.
    params: uploaded_file (Streamlit UploadedFile)
    returns: str (Extracted Text)
    """
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'pdf':
            return _extract_pdf(uploaded_file)
        elif file_type in ['docx', 'doc']:
            return _extract_docx(uploaded_file)
        elif file_type in ['pptx', 'ppt']:
            return _extract_pptx(uploaded_file)
        elif file_type in ['xlsx', 'xls']:
            return _extract_excel(uploaded_file)
        elif file_type == 'csv':
             df = pd.read_csv(uploaded_file)
             return df.to_string()
        elif file_type in ['txt', 'md', 'py', 'json']:
            return str(uploaded_file.read().decode("utf-8"))
        # Image support will be direct processing in QA engine for multimodal,
        # but for text extraction we can try simple OCR later if needed.
        # For now, return a placeholder for images saying "IMAGE_CONTENT" 
        # so the QA engine knows to treat it as an image input.
        elif file_type in ['png', 'jpg', 'jpeg']:
            return "Valid Image File" 
        else:
            return f"Unsupported file type: {file_type}"
    except Exception as e:
        return f"Error extracting file: {str(e)}"

def _extract_pdf(file):
    pdf = pypdf.PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

def _extract_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def _extract_pptx(file):
    prs = pptx.Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

def _extract_excel(file):
    # Convert to string representation
    df = pd.read_excel(file)
    return df.to_string()
