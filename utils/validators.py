import pandas as pd
import io
from typing import Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_csv_file(file) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded CSV file.
    
    Args:
        file: File object from request.files
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "File has no name"
    
    # Check file extension
    if not file.filename.lower().endswith('.csv'):
        return False, f"Invalid file type. Expected .csv, got {file.filename.split('.')[-1]}"
    
    # Check file size (max 10MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        return False, f"File too large. Maximum size is 10MB, got {file_size / (1024*1024):.2f}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, None


def validate_csv_content(file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Validate CSV file content and return DataFrame.
    
    Args:
        file: File object from request.files
        
    Returns:
        Tuple of (dataframe, error_message)
    """
    try:
        # Try to read CSV
        df = pd.read_csv(file)
        
        # Check if DataFrame is empty
        if df.empty:
            return None, "CSV file contains no data"
        
        # Check if DataFrame has columns
        if len(df.columns) == 0:
            return None, "CSV file has no columns"
        
        # Check for minimum rows
        if len(df) < 1:
            return None, "CSV file must contain at least 1 row of data"
        
        # Check for maximum rows (prevent memory issues)
        max_rows = 10000
        if len(df) > max_rows:
            return None, f"CSV file has too many rows. Maximum is {max_rows}, got {len(df)}"
        
        return df, None
        
    except pd.errors.EmptyDataError:
        return None, "CSV file is empty or malformed"
    except pd.errors.ParserError as e:
        return None, f"Failed to parse CSV file: {str(e)}"
    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}"


def validate_prompt(prompt: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user prompt.
    
    Args:
        prompt: User input prompt
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"
    
    # Check minimum length
    if len(prompt.strip()) < 10:
        return False, "Prompt is too short. Please provide a more detailed description (at least 10 characters)"
    
    # Check maximum length
    max_length = 5000
    if len(prompt) > max_length:
        return False, f"Prompt is too long. Maximum length is {max_length} characters, got {len(prompt)}"
    
    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
