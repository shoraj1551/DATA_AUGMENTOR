"""
Knowledge Base Builder UI
Project memory and natural language querying
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from tools.knowledge_base.ingestor import ContentIngestor
from tools.knowledge_base.qa_interface import QAInterface


def render():
    """Render the Knowledge Base Builder page"""
    render_page_header(
        title="Knowledge Base Builder",
        subtitle="Capture project knowledge and query with natural language",
        icon="🧠",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - Experimental feature. Feedback welcome!")
    
    # Initialize
    if 'kb_ingestor' not in st.session_state:
        st.session_state.kb_ingestor = ContentIngestor()
    if 'qa_interface' not in st.session_state:
        st.session_state.qa_interface = QAInterface()
    
    ingestor = st.session_state.kb_ingestor
    qa = st.session_state.qa_interface
    
    # Stats
    stats = ingestor.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Entries", stats['total_entries'])
    with col2:
        st.metric("Categories", stats['categories'])
    with col3:
        st.metric("Tags", stats['tags'])
    with col4:
        if stats['latest_entry']:
            st.metric("Latest", stats['latest_entry'].split()[0])
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "➕ Add Knowledge", "📚 Browse"])
    
    # Tab 1: Ask Questions
    with tab1:
        st.markdown("### 💬 Ask a Question")
        question = st.text_input(
            "What would you like to know?",
            placeholder="e.g., How does the authentication system work?"
        )
        
        if question and st.button("🔍 Search & Answer", type="primary"):
            with st.spinner("Searching knowledge base..."):
                # Search for relevant entries
                results = ingestor.search_entries(query=question)
                
                if results:
                    with st.spinner("Generating answer..."):
                        answer = qa.answer_question(question, results)
                        
                        st.markdown("### 💡 Answer")
                        st.success(answer['answer'])
                        
                        st.markdown(f"*Based on {answer['context_count']} knowledge base entries*")
                        
                        # Show sources
                        with st.expander("📖 View Sources"):
                            for entry in results[:5]:
                                st.markdown(f"**[{entry['category']}]** {entry['content'][:200]}...")
                                st.caption(f"Added: {entry['created_at']}")
                                st.markdown("---")
                else:
                    st.warning("No relevant knowledge found. Try adding more entries!")
        
        # Onboarding Guide
        st.markdown("---")
        if st.button("📘 Generate Onboarding Guide"):
            with st.spinner("Creating onboarding guide..."):
                all_entries = ingestor.search_entries()
                if all_entries:
                    guide = qa.generate_onboarding_guide(all_entries)
                    st.markdown("### 📘 Onboarding Guide")
                    st.markdown(guide)
                else:
                    st.warning("No knowledge entries yet. Add some first!")
    
    # Tab 2: Add Knowledge
    with tab2:
        st.markdown("### ➕ Add Knowledge Entry")
        
        content = st.text_area(
            "Content",
            height=150,
            placeholder="Paste code, documentation, decision notes, etc."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "Category",
                options=['code', 'documentation', 'decision', 'query', 'dashboard', 'ticket', 'other']
            )
        
        with col2:
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="authentication, api, database"
            )
        
        metadata_input = st.text_area(
            "Metadata (JSON, optional)",
            height=80,
            placeholder='{"author": "John", "project": "DataAugmentor"}'
        )
        
        if st.button("💾 Save Entry", type="primary", disabled=not content):
            tags = [t.strip() for t in tags_input.split(',') if t.strip()]
            
            metadata = {}
            if metadata_input.strip():
                try:
                    metadata = json.loads(metadata_input)
                except:
                    st.error("Invalid JSON in metadata")
                    return
            
            entry = ingestor.add_entry(content, category, tags, metadata)
            st.success(f"✅ Entry #{entry['id']} added successfully!")
            st.rerun()
    
    # Tab 3: Browse
    with tab3:
        st.markdown("### 📚 Browse Knowledge Base")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox(
                "Filter by Category",
                options=['All'] + ingestor.get_all_categories()
            )
        with col2:
            filter_tags = st.multiselect(
                "Filter by Tags",
                options=ingestor.get_all_tags()
            )
        
        search_text = st.text_input("Search", placeholder="Search in content...")
        
        # Get entries
        entries = ingestor.search_entries(
            query=search_text if search_text else None,
            category=filter_category if filter_category != 'All' else None,
            tags=filter_tags if filter_tags else None
        )
        
        st.markdown(f"**Found {len(entries)} entries**")
        
        # Display entries
        for entry in reversed(entries):  # Show newest first
            with st.expander(f"#{entry['id']} - {entry['category'].upper()} - {entry['created_at']}"):
                st.markdown(entry['content'])
                
                if entry.get('tags'):
                    st.caption(f"Tags: {', '.join(entry['tags'])}")
                
                if entry.get('metadata'):
                    st.json(entry['metadata'])
                
                if st.button(f"🗑️ Delete", key=f"del_{entry['id']}"):
                    ingestor.delete_entry(entry['id'])
                    st.success("Entry deleted!")
                    st.rerun()
    
    # Export
    st.markdown("---")
    st.markdown("## 📥 Export Knowledge Base")
    
    all_entries = ingestor.search_entries()
    if all_entries:
        export_data = json.dumps(all_entries, indent=2)
        st.download_button(
            label="📥 Download Full Knowledge Base (JSON)",
            data=export_data,
            file_name="knowledge_base.json",
            mime="application/json",
            use_container_width=True
        )
