"""
Document Parser & Intelligence UI Module (V2)
"""
import streamlit as st
import pandas as pd
import os
from app_components.navigation import back_to_home
from document_parser import extractor, qa_engine, structure_engine, rag_engine

def render():
    back_to_home("DocumentParser")
    st.markdown('<h2 class="main-header">Document Intelligence <span style="background:#2563eb; color:white; font-size:0.4em; vertical-align:middle; padding:2px 8px; border-radius:10px;">V2</span></h2>', unsafe_allow_html=True)
    
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
            uploaded_files = st.file_uploader(
                "Select files (PDF, Docx, Excel, PPT, Txt)", 
                type=['pdf', 'docx', 'doc', 'pptx', 'xlsx', 'csv', 'txt', 'md', 'json', 'png', 'jpg'],
                accept_multiple_files=True
            )
            if uploaded_files:
                if st.button("Process Files", type="primary"):
                    files_to_process = [(f, f.name) for f in uploaded_files]

        else: # Local Folder
            folder_path = st.text_input("Enter Folder Path:", placeholder=r"C:\Users\Name\Documents\Reports")
            if st.button("Load Folder", type="primary"):
                if os.path.isdir(folder_path):
                     valid_exts = ['.pdf', '.docx', '.doc', '.pptx', '.xlsx', '.csv', '.txt', '.md', '.json']
                     for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in valid_exts):
                                full_path = os.path.join(root, file)
                                files_to_process.append((full_path, file))
                     
                     if not files_to_process:
                         st.error("No supported files found in this folder.")
                else:
                    st.error("Invalid Folder Path")
        
        # --- PROCESSING LOGIC ---
        if files_to_process:
            with st.status("Processing Documents..."):
                st.write("Extracting text...")
                texts = []
                names = []
                full_text_concat = ""
                
                progress_bar = st.progress(0)
                for i, (f_obj, fname) in enumerate(files_to_process):
                    try:
                        txt = extractor.extract_text_from_file(f_obj)
                        texts.append(txt)
                        names.append(fname)
                        full_text_concat += f"\n--- File: {fname} ---\n{txt}"
                    except Exception as e:
                        st.warning(f"Failed to load {fname}: {e}")
                    progress_bar.progress((i + 1) / len(files_to_process))
                
                st.write("Building Knowledge Base (RAG Index)...")
                st.session_state.kb.add_documents(texts, names)
                st.session_state.doc_loaded = True
                
                st.write("Generating Insights...")
                if len(full_text_concat) > 0:
                     st.session_state.story_highlights = qa_engine.generate_story_highlights(full_text_concat)
                
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
                with st.spinner("Analyzing schema..."):
                    # Sample first 50k chars
                    sample_text = "".join(st.session_state.kb.documents)[:50000]
                    fields = structure_engine.suggest_schema(sample_text)
                    st.session_state.suggested_fields = fields
            
            if st.session_state.suggested_fields:
                st.caption("Found Fields:")
                for f in st.session_state.suggested_fields:
                    st.code(f, language="text")
        
        with c_req:
            reqs = st.text_area("Extraction Requirements:", placeholder="e.g. Extract Invoice Date, Amount, and Vendor.")
            
            if st.button("Run Extraction 🚀", type="primary"):
                if reqs:
                    with st.spinner("Extracting..."):
                        # Use all context for extraction (Gemini 1M handles it)
                        full_context = "\n".join(st.session_state.kb.documents)
                        try:
                            dfs = structure_engine.parse_structured_data(full_context, reqs)
                            st.success(f"✅ Extracted {len(dfs)} tables.")
                            for name, df in dfs:
                                with st.expander(f"Dataset: {name}", expanded=True):
                                    st.dataframe(df)
                                    st.download_button(f"Download {name}.csv", df.to_csv(index=False).encode('utf-8'), f"{name}.csv")
                        except Exception as e:
                            st.error(f"Failed: {e}")
