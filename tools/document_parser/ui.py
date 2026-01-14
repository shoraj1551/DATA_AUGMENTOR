"""
Document Parser & Intelligence UI Module (V2)
"""
import streamlit as st
import pandas as pd
import os
from common.ui.navigation import render_page_header
from document_parser import extractor, qa_engine, structure_engine, rag_engine

def render():
    render_page_header(
        title="Text Document Parser",
        subtitle="Extract text from PDF, TXT, and PowerPoint files (OCR tool coming soon for images)",
        icon="📄",
        status="beta"
    )
    
    # --- Session State ---
    if "kb" not in st.session_state:
        st.session_state.kb = rag_engine.DocumentKnowledgeBase()
    if "doc_loaded" not in st.session_state:
        st.session_state.doc_loaded = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "story_highlights" not in st.session_state:
        st.session_state.story_highlights = []
    if "parser_mode" not in st.session_state:
        st.session_state.parser_mode = None 
    if "suggested_fields" not in st.session_state:
        st.session_state.suggested_fields = []

    # --- LANDING SCREEN (Choice First) ---
    if not st.session_state.doc_loaded:
        st.subheader("🚀 Start New Session")
        
        input_method = st.radio("Choose Input Method:", ["📄 Upload Single/Multiple Files", "📁 Load Local Folder"], horizontal=True)
        
        files_to_process = []
        
        if "Upload" in input_method:
            st.info("📌 **Supported formats:** PDF, TXT, PPTX. For images, use the OCR tool (coming soon).")
            uploaded_files = st.file_uploader(
                "Select files (PDF, TXT, PowerPoint)", 
                type=['pdf', 'txt', 'pptx'],
                accept_multiple_files=True,
                help="Upload PDF, text, or PowerPoint files only"
            )
            if uploaded_files:
                if st.button("Process Files", type="primary"):
                    files_to_process = [(f, f.name) for f in uploaded_files]

        else: # Local Folder
            folder_path = st.text_input("Enter Folder Path:", placeholder=r"C:\Users\Name\Documents\Reports")
            
            col1, col2 = st.columns(2)
            with col1:
                max_files = st.number_input("Max Files to Load", min_value=1, max_value=100, value=20, help="Limit number of files to prevent long loading times")
            with col2:
                include_subfolders = st.checkbox("Include Subfolders", value=False, help="Search in subdirectories (may be slower)")
            
            if st.button("Load Folder", type="primary"):
                if os.path.isdir(folder_path):
                    valid_exts = ['.pdf', '.docx', '.doc', '.pptx', '.xlsx', '.csv', '.txt', '.md', '.json']
                    file_count = 0
                    
                    if include_subfolders:
                        # Walk through subdirectories
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                if file_count >= max_files:
                                    break
                                if any(file.lower().endswith(ext) for ext in valid_exts):
                                    full_path = os.path.join(root, file)
                                    files_to_process.append((full_path, file))
                                    file_count += 1
                            if file_count >= max_files:
                                break
                    else:
                        # Only current folder (faster)
                        for file in os.listdir(folder_path):
                            if file_count >= max_files:
                                break
                            if any(file.lower().endswith(ext) for ext in valid_exts):
                                full_path = os.path.join(folder_path, file)
                                if os.path.isfile(full_path):
                                    files_to_process.append((full_path, file))
                                    file_count += 1
                    
                    if not files_to_process:
                        st.error("No supported files found in this folder.")
                    elif file_count >= max_files:
                        st.warning(f"⚠️ Reached maximum file limit ({max_files}). Only first {max_files} files will be loaded.")
                else:
                    st.error("Invalid Folder Path")
        
        # --- PROCESSING LOGIC ---
        if files_to_process:
            with st.status("Processing Documents...", expanded=True):
                st.write(f"📁 Found {len(files_to_process)} file(s) to process")
                texts = []
                names = []
                full_text_concat = ""
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, (f_obj, fname) in enumerate(files_to_process):
                    try:
                        status_text.text(f"Processing {i+1}/{len(files_to_process)}: {fname}")
                        txt = extractor.extract_text_from_file(f_obj)
                        texts.append(txt)
                        names.append(fname)
                        full_text_concat += f"\n--- File: {fname} ---\n{txt}"
                    except Exception as e:
                        st.warning(f"⚠️ Failed to load {fname}: {e}")
                    progress_bar.progress((i + 1) / len(files_to_process))
                
                st.write("🔍 Building Knowledge Base (RAG Index)...")
                st.session_state.kb.add_documents(texts, names)
                st.session_state.doc_loaded = True
                
                st.write("✨ Generating Insights...")
                if len(full_text_concat) > 0:
                     st.session_state.story_highlights = qa_engine.generate_story_highlights(full_text_concat)
                
                st.success(f"✅ Successfully loaded {len(texts)} document(s)!")
                st.rerun()
        return

    # --- MAIN INTERFACE (After Load) ---
    
    # Top Bar: Status & Reset
    c_status, c_reset = st.columns([0.85, 0.15])
    with c_status:
        st.success(f"✅ Knowledge Base Active: {len(st.session_state.kb.documents)} documents indexed.")
    with c_reset:
        if st.button("🔄 New Session", type="secondary"):
             st.session_state.kb = rag_engine.DocumentKnowledgeBase()
             st.session_state.doc_loaded = False
             st.session_state.chat_history = []
             st.session_state.parser_mode = None
             st.rerun()

    # Wizard Mode Selection
    if not st.session_state.parser_mode:
        st.markdown("### 🤖 Choose Action")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("💬 Chat Q&A\nAsk questions with RAG context", use_container_width=True, type="primary"):
                st.session_state.parser_mode = "chat"
                st.rerun()
        with col_m2:
            if st.button("📊 Data Extractor\nConvert to Tables", use_container_width=True, type="primary"):
                st.session_state.parser_mode = "extract"
                st.rerun()
        
        # Show Insights preview
        if st.session_state.story_highlights:
            st.divider()
            st.subheader("💡 Key Insights")
            for h in st.session_state.story_highlights:
                st.info(h)
        return

    # --- SPECIFIC MODES ---
    
    # Header & Back
    c_h1, c_h2 = st.columns([0.8, 0.2])
    with c_h1:
        st.subheader(f"Mode: {'Chat Q&A' if st.session_state.parser_mode == 'chat' else 'Data Extractor'}")
    with c_h2:
        if st.button("← Switch Action"):
            st.session_state.parser_mode = None
            st.rerun()
            
    st.divider()

    # === CHAT MODE ===
    if st.session_state.parser_mode == "chat":
        # Chat History
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if query := st.chat_input("Ask a question..."):
            st.session_state.chat_history.append({"role": "user", "content": query})
            with st.chat_message("user"): st.write(query)
            
            with st.chat_message("assistant"):
                with st.spinner("Retrieving Knowledge..."):
                    # RAG Retrieval
                    context = st.session_state.kb.get_context(query)
                    response = qa_engine.ask_document_question(context, st.session_state.chat_history[:-1], query)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # === EXTRACT MODE ===
    elif st.session_state.parser_mode == "extract":
        
        # Schema Discovery
        c_req, c_sug = st.columns([0.7, 0.3])
        
        with c_sug:
            if st.button("🔍 Analyze & Suggest Fields"):
                with st.spinner("Analyzing document structure..."):
                    # Sample first 50k chars
                    sample_text = "".join(st.session_state.kb.documents)[:50000]
                    fields, error_msg = structure_engine.suggest_schema(sample_text)
                    st.session_state.suggested_fields = fields
                    st.session_state.suggestion_error = error_msg
                    
                    # Auto-populate extraction requirements if fields found
                    if fields and len(fields) > 0:
                        st.session_state.auto_requirements = f"Extract: {', '.join(fields)}"
            
            # Display results below the button
            if 'suggestion_error' in st.session_state and st.session_state.suggestion_error:
                # Show error or no-fields message in a box
                st.warning(st.session_state.suggestion_error)
            elif st.session_state.suggested_fields:
                # Show found fields
                st.success(f"✅ Found {len(st.session_state.suggested_fields)} extractable fields:")
                for f in st.session_state.suggested_fields:
                    st.code(f, language="text")
        
        with c_req:
            # Pre-fill with suggested fields if available
            default_reqs = st.session_state.get('auto_requirements', '')
            reqs = st.text_area(
                "Extraction Requirements:", 
                value=default_reqs,
                placeholder="e.g. Extract Invoice Date, Amount, and Vendor. (Leave empty to auto-extract all structured data)",
                help="Specify what to extract, or leave empty to automatically extract all structured data found"
            )
            
            # Export format selection
            export_format = st.radio(
                "Export Format:",
                options=["Table (CSV)", "JSON"],
                horizontal=True,
                help="Choose how to export extracted data"
            )
            
            if st.button("Run Extraction 🚀", type="primary"):
                # Allow extraction even without requirements
                with st.spinner("Extracting data..."):
                    # Use all context for extraction (Gemini 1M handles it)
                    full_context = "\n".join(st.session_state.kb.documents)
                    
                    # If no requirements, use auto-extract mode
                    if not reqs or reqs.strip() == "":
                        if st.session_state.suggested_fields:
                            # Use suggested fields
                            reqs = f"Extract all available data for these fields: {', '.join(st.session_state.suggested_fields)}"
                        else:
                            # Generic extraction
                            reqs = "Extract all structured data, tables, and key-value pairs from this document"
                    
                    try:
                        dfs = structure_engine.parse_structured_data(full_context, reqs)
                        
                        if dfs and len(dfs) > 0:
                            st.success(f"✅ Extracted {len(dfs)} dataset(s).")
                            for name, df in dfs:
                                with st.expander(f"Dataset: {name}", expanded=True):
                                    # Preview based on selected format
                                    if export_format == "JSON":
                                        st.markdown("**JSON Preview:**")
                                        json_preview = df.to_dict(orient='records')
                                        st.json(json_preview)
                                    else:  # Table (CSV)
                                        st.markdown("**Table Preview:**")
                                        st.dataframe(df)
                                    
                                    # Export options based on selected format
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.download_button(
                                            f"📥 Download {name}.csv", 
                                            df.to_csv(index=False).encode('utf-8'), 
                                            f"{name}.csv",
                                            use_container_width=True
                                        )
                                    with col2:
                                        # JSON export
                                        json_data = df.to_json(orient='records', indent=2)
                                        st.download_button(
                                            f"📥 Download {name}.json", 
                                            json_data.encode('utf-8'), 
                                            f"{name}.json",
                                            mime="application/json",
                                            use_container_width=True
                                        )
                        else:
                            st.warning("⚠️ No structured data found in the document. The document may contain only unstructured text.")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")
