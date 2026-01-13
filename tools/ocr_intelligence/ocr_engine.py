"""
OCR Engine - Text extraction from images using Tesseract
"""
import io
from PIL import Image
import pytesseract
from typing import Dict, Optional


class OCREngine:
    """OCR processing engine using Tesseract"""
    
    def __init__(self):
        """Initialize OCR engine"""
        # Set Tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text(
        self, 
        image_bytes: bytes, 
        language: str = 'eng',
        preserve_layout: bool = False
    ) -> Dict[str, any]:
        """
        Extract text from image
        
        Args:
            image_bytes: Image file bytes
            language: OCR language code (eng, spa, fra, etc.)
            preserve_layout: Preserve original text layout
            
        Returns:
            Dict with extracted text, confidence, and metadata
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            if preserve_layout:
                text = pytesseract.image_to_string(image, lang=language)
            else:
                text = pytesseract.image_to_string(image, lang=language)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'word_count': len(text.split()),
                'char_count': len(text),
                'language': language
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        try:
            langs = pytesseract.get_languages()
            return langs
        except:
            return ['eng']  # Default to English if detection fails
