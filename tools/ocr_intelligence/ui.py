"""
OCR Image Intelligence UI
Professional interface for image text extraction
"""
import streamlit as st
import io
from PIL import Image
from common.ui.navigation import render_page_header
from tools.ocr_intelligence.ocr_engine import OCREngine


def render():
    """Render the OCR Image Intelligence page"""
    render_page_header(
        title="OCR Image Intelligence",
        subtitle="Extract text from images and scanned documents with AI-powered OCR",
        icon="🖼️",
        status="new"
    )
    
    # Check Tesseract installation
    if 'tesseract_checked' not in st.session_state:
        st.session_state.tesseract_checked = False
        st.session_state.tesseract_available = False
    
    if not st.session_state.tesseract_checked:
        from tools.ocr_intelligence.installer import TesseractInstaller
        
        with st.spinner("Checking Tesseract OCR installation..."):
            installer = TesseractInstaller()
            
            if not installer.check_installation():
                st.warning("⚠️ Tesseract OCR not found. Attempting automatic installation...")
                
                with st.spinner("Installing Tesseract OCR... This may take a few minutes."):
                    result = installer.install()
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.session_state.tesseract_available = True
                    st.info("🔄 Please refresh the page to use OCR features.")
                else:
                    st.error(f"❌ {result['message']}")
                    if 'manual_instructions' in result:
                        st.markdown("### Manual Installation Required")
                        st.markdown(result['manual_instructions'])
                    st.session_state.tesseract_available = False
            else:
                st.session_state.tesseract_available = True
            
            st.session_state.tesseract_checked = True
    
    # Only show OCR interface if Tesseract is available
    if not st.session_state.tesseract_available:
        st.error("❌ Tesseract OCR is not available. Please install it manually using the instructions above.")
        return
    
    # Initialize OCR engine
    if 'ocr_engine' not in st.session_state:
        st.session_state.ocr_engine = OCREngine()
    
    # Initialize session state
    if 'ocr_result' not in st.session_state:
        st.session_state.ocr_result = None
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    
    # File Upload Section
    st.markdown("### 📤 Upload Images")
    st.info("📌 **Supported formats:** PNG, JPG, JPEG, TIFF, BMP, WEBP (Max 10MB per image)")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'],
        help="Upload an image containing text to extract"
    )
    
    if uploaded_file:
        # Store uploaded image
        st.session_state.uploaded_image = uploaded_file
        
        # Display image preview
        st.markdown("### 🔍 Image Preview")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        with col2:
            # OCR Settings
            st.markdown("### ⚙️ OCR Settings")
            
            language = st.selectbox(
                "Language",
                options=['eng', 'spa', 'fra', 'deu', 'ita', 'por'],
                format_func=lambda x: {
                    'eng': 'English',
                    'spa': 'Spanish',
                    'fra': 'French',
                    'deu': 'German',
                    'ita': 'Italian',
                    'por': 'Portuguese'
                }.get(x, x),
                help="Select the language of text in the image"
            )
            
            preserve_layout = st.checkbox(
                "Preserve text layout",
                value=False,
                help="Maintain original text formatting"
            )
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Extract button
            if st.button("🔍 Extract Text", type="primary", use_container_width=True):
                with st.spinner("Extracting text from image..."):
                    # Read image bytes
                    image_bytes = uploaded_file.getvalue()
                    
                    # Perform OCR
                    result = st.session_state.ocr_engine.extract_text(
                        image_bytes=image_bytes,
                        language=language,
                        preserve_layout=preserve_layout
                    )
                    
                    st.session_state.ocr_result = result
        
        # Display Results
        if st.session_state.ocr_result:
            result = st.session_state.ocr_result
            
            st.markdown("---")
            st.markdown("### 📄 Extracted Text")
            
            if result['success']:
                # Confidence and stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence", f"{result['confidence']}%")
                with col2:
                    st.metric("Words", result['word_count'])
                with col3:
                    st.metric("Characters", result['char_count'])
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                # Extracted text
                if result['text']:
                    st.text_area(
                        "Extracted Text",
                        value=result['text'],
                        height=300,
                        help="Copy this text or download it below"
                    )
                    
                    # Download buttons
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        st.download_button(
                            label="📥 Download TXT",
                            data=result['text'],
                            file_name="extracted_text.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        # JSON export
                        import json
                        json_data = json.dumps(result, indent=2)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_data,
                            file_name="ocr_result.json",
                            mime="application/json",
                            use_container_width=True
                        )
                else:
                    st.warning("⚠️ No text detected in the image. Try adjusting the image quality or language settings.")
            else:
                st.error(f"❌ OCR failed: {result.get('error', 'Unknown error')}")
    
    else:
        # Empty state
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.info("👆 Upload an image to get started with text extraction!")
        
        # Example use cases
        st.markdown("### 💡 Use Cases")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📄 Documents**
            - Scanned PDFs
            - Book pages
            - Handwritten notes
            """)
        
        with col2:
            st.markdown("""
            **🧾 Business**
            - Receipts
            - Invoices
            - Business cards
            """)
        
        with col3:
            st.markdown("""
            **📊 Data**
            - Tables & charts
            - Screenshots
            - Whiteboards
            """)
