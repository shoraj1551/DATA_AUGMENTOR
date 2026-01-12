"""
Document Parser & Intelligence UI Module
"""
import streamlit as st
import pandas as pd
from components.navigation import back_to_home
from document_parser import extractor, qa_engine, structure_engine

def render():
    back_to_home("DocumentParser")
    st.markdown('<h2 class="main-header">Document Intelligence <span style="background:#2563eb; color:white; font-size:0.4em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Chat with documents or extract structured data tables.</p>', unsafe_allow_html=True)

    # --- Session State ---
    if "doc_text" not in st.session_state:
        st.session_state.doc_text = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "story_highlights" not in st.session_state:
        st.session_state.story_highlights = []
    if "parser_mode" not in st.session_state:
        st.session_state.parser_mode = None # 'chat' or 'extract' or None
        
    # --- Main Layout (No Sidebar) ---
    
    # 1. Document Input Section
    with st.container():
        st.subheader("📂 Document Input")
        
        # Tabs for input method
        tab_upload, tab_folder = st.tabs(["📄 File Upload", "📁 Local Folder"])
        
        # --- TAB 1: Streamlit Uploader ---
        with tab_upload:
            col_up, col_reset = st.columns([0.85, 0.15])
            with col_up:
                uploaded_files = st.file_uploader(
                    "Select files (drag & drop)", 
                    type=['pdf', 'docx', 'doc', 'pptx', 'xlsx', 'csv', 'txt', 'md', 'json', 'png', 'jpg'],
                    accept_multiple_files=True,
                    label_visibility="collapsed",
                    key="uploader_widget"
                )
            with col_reset:
                if st.button("🔄 Reset", key="reset_upload", type="secondary", help="Clear session"):
                     st.session_state.doc_text = ""
                     st.session_state.chat_history = []
                     st.session_state.question_count = 0
                     st.session_state.story_highlights = []
                     st.session_state.parser_mode = None
                     st.rerun()

        # --- TAB 2: Local Folder Input ---
        with tab_folder:
            col_path, col_btn = st.columns([0.8, 0.2])
            with col_path:
                folder_path = st.text_input("Enter local folder path:", placeholder=r"C:\Users\Name\Documents\ProjectX")
            with col_btn:
                load_folder = st.button("Load Folder", type="primary", use_container_width=True)
            
            if load_folder and folder_path:
                import os
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    with st.spinner(f"Scanning {folder_path}..."):
                        found_files = []
                        valid_exts = ['.pdf', '.docx', '.doc', '.pptx', '.xlsx', '.csv', '.txt', '.md', '.json']
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                if any(file.lower().endswith(ext) for ext in valid_exts):
                                    found_files.append(os.path.join(root, file))
                        
                        if found_files:
                            st.success(f"Found {len(found_files)} documents. Processing...")
                            full_text = ""
                            # Limit to avoiding freezing (e.g. max 20 files for now or just process all)
                            # For safety let's process up to 20 files
                            processed_count = 0
                            for fp in found_files: # Process all
                                try:
                                    text = extractor.extract_text_from_file(fp)
                                    full_text += f"\n--- File: {os.path.basename(fp)} ---\n{text}"
                                    processed_count += 1
                                except Exception as e:
                                    st.warning(f"Skipped {os.path.basename(fp)}: {e}")
                                    
                            st.session_state.doc_text = full_text
                            
                            # Generate Story
                            if full_text.strip():
                                highlights = qa_engine.generate_story_highlights(full_text)
                                st.session_state.story_highlights = highlights
                            
                            st.rerun()
                        else:
                            st.warning("No supported files found in this directory.")
                else:
                    st.error("Invalid Directory Path.")


    # --- Processing Logic (for Tab 1 Uploader) ---
    if uploaded_files and not st.session_state.doc_text:
        with st.spinner("Processing uploaded documents..."):
            full_text = ""
            for f in uploaded_files:
                text = extractor.extract_text_from_file(f)
                full_text += f"\n--- File: {f.name} ---\n{text}"
            
            st.session_state.doc_text = full_text
            
            # Generate Story if text exists
            if full_text.strip():
                highlights = qa_engine.generate_story_highlights(full_text)
                st.session_state.story_highlights = highlights
            
            st.rerun()

    # --- Main Interface Flow ---
    
    # 1. No Documents
    if not st.session_state.doc_text:
         # Show feature preview cards (Non-interactive until upload)
        c1, c2 = st.columns(2)
        with c1:
            st.warning("💬 **Chat Q&A**: Ask questions to your PDF/Docs")
        with c2:
            st.warning("📊 **Data Extractor**: Convert Unstructured files to Tables")
        return

    # 2. Documents Uploaded but No Mode Selected (WIZARD STEP)
    if not st.session_state.parser_mode:
        st.divider()
        st.subheader("🤖 How would you like to process these documents?")
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            with st.container(border=True):
                st.markdown("### 💬 Chat Q&A")
                st.write("Interact with your documents like a chatbot. Ask questions, get summaries, and find insights.")
                if st.button("Start Chat Session", use_container_width=True, type="primary"):
                    st.session_state.parser_mode = "chat"
                    st.rerun()
                    
        with col_m2:
             with st.container(border=True):
                st.markdown("### 📊 Data Extractor")
                st.write("Turn unstructured text/PDFs into clean Excel/CSV tables based on your requirements.")
                if st.button("Start Extraction", use_container_width=True, type="primary"):
                    st.session_state.parser_mode = "extract"
                    st.rerun()
        return

    # 3. specific Mode Interface
    
    # Header with Back Button
    c_head1, c_head2 = st.columns([0.8, 0.2])
    with c_head1:
        mode_label = "💬 Chat Q&A" if st.session_state.parser_mode == "chat" else "📊 Data Extractor"
        st.subheader(f"Mode: {mode_label}")
    with c_head2:
        if st.button("← Switch Mode"):
            st.session_state.parser_mode = None
            st.rerun()
            
    st.divider()

    # --- CHAT MODE ---
    if st.session_state.parser_mode == "chat":
        # Two Column Layout (Left: Story, Right: Main)
        col_story, col_main = st.columns([1, 2.5])
        
        # === Story / Knowledge Base Side ===
        with col_story:
            st.markdown("#### 💡 Key Insights")
            if st.session_state.story_highlights:
                for i, highlight in enumerate(st.session_state.story_highlights):
                    st.info(f"**{i+1}.** {highlight}")
            else:
                st.caption("No highlights generated.")

        # === Main Interaction Side ===
        with col_main:
            # Limit check
            if st.session_state.question_count >= 20:
                st.error("🛑 Question limit reached (20/20). Please reset the session to ask more.")
            else:
                st.caption(f"Questions Used: {st.session_state.question_count} / 20")
                
                # Chat History
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                
                # Input
                if query := st.chat_input("Ask a question about your documents..."):
                    # Add User Message
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    st.session_state.question_count += 1
                    with st.chat_message("user"):
                        st.write(query)
                    
                    # Get AI Response
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = qa_engine.ask_document_question(
                                st.session_state.doc_text,
                                st.session_state.chat_history[:-1],
                                query
                            )
                            st.write(response)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                            st.rerun()

    # --- EXTRACTOR MODE ---
    elif st.session_state.parser_mode == "extract":
        st.markdown("#### Describe the data you want to extract")
        
        reqs = st.text_area("Extraction Requirements:", placeholder="e.g. Extract a list of all invoice items with Date, Description, Quantity, and Total Amount.")
        
        if st.button("Run Extraction 🚀", type="primary"):
            if reqs:
                with st.spinner("Parsing documents into structured format..."):
                    try:
                        dfs = structure_engine.parse_structured_data(st.session_state.doc_text, reqs)
                        
                        st.success(f"✅ Extracted {len(dfs)} table(s).")
                        
                        for name, df in dfs:
                            with st.expander(f"Table: {name}", expanded=True):
                                st.dataframe(df, use_container_width=True)
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    f"📥 Download {name}.csv",
                                    csv,
                                    f"{name}.csv",
                                    "text/csv"
                                )
                    except Exception as e:
                        st.error(f"Extraction Failed: {str(e)}")
            else:
                st.warning("Please enter requirements.")
