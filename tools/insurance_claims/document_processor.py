"""
Document Processor for Insurance Claims
Independent module to handle file extraction specifically for this tool.
"""
import io
import pypdf
import pandas as pd
import streamlit as st

def extract_text_from_file(file_input) -> str:
    """
    Extract text from uploaded file (PDF or TXT).
    Args:
        file_input: Streamlit UploadedFile object or file path
    Returns:
        str: Extracted text
    """
    try:
        # Handle Streamlit UploadedFile
        filename = file_input.name
        file_type = filename.split('.')[-1].lower()
        
        if file_type == 'pdf':
            return _extract_pdf(file_input)
        elif file_type == 'txt':
            return file_input.read().decode('utf-8')
        else:
            return f"Unsupported file type: {file_type}. Please upload PDF or TXT."
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

def _extract_pdf(file_obj) -> str:
    """Extract text from PDF"""
    try:
        pdf_reader = pypdf.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"PDF Extraction Failed: {str(e)}")
