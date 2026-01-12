"""
Document Parser & Intelligence UI Module
"""
import streamlit as st
import pandas as pd
from components.navigation import back_to_home
from document_parser import extractor, qa_engine, structure_engine

def render():
    back_to_home("DocumentParser")
    st.markdown('<h2 class="main-header">Document Intelligence <span style="background:#8b5cf6; color:white; font-size:0.4em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h2>', unsafe_allow_html=True)
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
        
    # --- Sidebar Controls ---
    with st.sidebar:
        st.header("📂 Document Input")
        uploaded_files = st.file_uploader(
            "Upload Files (PDF, Docx, Excel, PPT, Txt)", 
            type=['pdf', 'docx', 'doc', 'pptx', 'xlsx', 'csv', 'txt', 'md', 'json', 'png', 'jpg'],
            accept_multiple_files=True
        )
        
        mode = st.radio("Select Mode", ["💬 Chat Q&A", "📊 Data Extractor"], index=0)
        
        if st.button("🔄 Reset Session", type="secondary"):
            st.session_state.doc_text = ""
            st.session_state.chat_history = []
            st.session_state.question_count = 0
            st.session_state.story_highlights = []
            st.rerun()

    # --- Processing Logic ---
    if uploaded_files and not st.session_state.doc_text:
        with st.spinner("Processing documents & Generating Story..."):
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

    # --- Main Interface ---
    if not st.session_state.doc_text:
        st.info("👈 Upload documents in the sidebar to begin.")
        return

    # Two Column Layout (Left: Story, Right: Main)
    col_story, col_main = st.columns([1, 2.5])
    
    # === Story / Knowledge Base Side ===
    with col_story:
        st.subheader("💡 Knowledge Story")
        if st.session_state.story_highlights:
            for i, highlight in enumerate(st.session_state.story_highlights):
                st.info(f"**{i+1}.** {highlight}")
        else:
            st.caption("No highlights generated.")

    # === Main Interaction Side ===
    with col_main:
        if mode == "💬 Chat Q&A":
            st.subheader("Chat with Context")
            
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

        elif mode == "📊 Data Extractor":
            st.subheader("Structured Data Extraction")
            st.markdown("Describe the table or data fields you want to extract.")
            
            reqs = st.text_area("Extraction Requirements:", placeholder="Extract all invoice items with Date, Item Name, and Amount.")
            
            if st.button("Extract Data", type="primary"):
                if reqs:
                    with st.spinner("Parsing documents into structured format..."):
                        try:
                            dfs = structure_engine.parse_structured_data(st.session_state.doc_text, reqs)
                            
                            st.success(f"Extracted {len(dfs)} table(s).")
                            
                            for name, df in dfs:
                                with st.expander(f"Table: {name}", expanded=True):
                                    st.dataframe(df)
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
