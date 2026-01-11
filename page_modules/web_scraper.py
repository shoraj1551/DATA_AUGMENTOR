"""
Web Data Scraper Page Module
"""
import streamlit as st
import pandas as pd
import json
from components.navigation import back_to_home
from web_scraper import validator, fetcher, parser

def render():
    """Render the Web Data Scraper page"""
    back_to_home("WebScraper")
    st.markdown('<h2 class="main-header">Web Data Scraper <span style="background:#2563eb; color:white; font-size:0.4em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract structured data from web pages compliant with robots.txt</p>', unsafe_allow_html=True)
    
    # Input Section
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            url = st.text_input("Enter Website URL:", placeholder="https://example.com/data")
        with col2:
            st.write("") # Spacer
            st.write("")
            scrape_btn = st.button("🚀 Check & Scrape", type="primary", use_container_width=True)
    
    if scrape_btn and url:
        if not url.startswith("http"):
            st.error("Please enter a valid URL starting with http:// or https://")
            return

        with st.status("Processing...", expanded=True) as status:
            # 1. Compliance Check
            st.write("🔍 Checking robots.txt compliance...")
            is_allowed = validator.is_scraping_allowed(url)
            
            if not is_allowed:
                status.update(label="Scraping Disallowed", state="error")
                st.error(f"🛑 Scraping is disallowed by the website's robots.txt policy for this URL.")
                st.info("We respect website policies to ensure ethical scraping.")
                return
            
            st.write("✅ Compliance check passed.")
            
            # 2. Fetch Content
            st.write("🌐 Fetching content...")
            try:
                html = fetcher.fetch_content(url)
                st.write(f"✅ Content fetched ({len(html)} chars).")
            except Exception as e:
                status.update(label="Fetch Failed", state="error")
                st.error(f"Failed to fetch content: {str(e)}")
                return
            
            # 3. Parse Content
            st.write("📊 Parsing data...")
            
            # --- AI Extraction Logic ---
            try:
                # Always try basic table extraction first
                tables = parser.extract_tables(html)
                metadata = parser.extract_metadata(html)
                
                ai_data = []
                use_ai = st.toggle("Use AI to structure data?", value=True, help="Use Gemini 2.0 Flash to intelligently parse content into JSON")
                
                if use_ai:
                    st.write("🤖 AI is analyzing content structure...")
                    from web_scraper import ai_extractor
                    ai_data = ai_extractor.extract_structured_data(html, url)
                    st.write(f"✅ AI found {len(ai_data)} items.")
                
            except Exception as e:
                status.update(label="Processing Failed", state="error")
                st.error(f"Failed to process content: {str(e)}")
                return
            
            status.update(label="Completed Successfully!", state="complete", expanded=False)
        
        # === RESULTS DISPLAY ===
        st.divider()
        
        # Metadata
        st.subheader("Page Info")
        st.info(f"**Title**: {metadata['title']}\n\n**Description**: {metadata['description']}")
        
        # AI Result Display
        if use_ai and ai_data:
            st.subheader(f"🤖 AI Extracted Data ({len(ai_data)} items)")
            
            # Convert to DataFrame for easy view
            ai_df = pd.DataFrame(ai_data)
            st.dataframe(ai_df, use_container_width=True)
            
            # Download AI Data
            json_str = json.dumps(ai_data, indent=2)
            st.download_button(
                label="📥 Download AI Data (JSON)",
                data=json_str,
                file_name="ai_scraped_data.json",
                mime="application/json",
                key="dl_ai"
            )
            st.divider()

        # Regular Table Display
        if tables:
            st.subheader(f"Raw HTML Tables ({len(tables)})")
            
            for i, df in enumerate(tables):
                with st.expander(f"Dataset #{i+1} ({len(df)} rows)", expanded=(i==0)):
                    # Preview
                    st.dataframe(df, use_container_width=True)
                    
                    # Convert to JSON
                    json_str = df.to_json(orient="records", indent=2)
                    
                    col_d1, col_d2 = st.columns([1, 4])
                    with col_d1:
                        # Download Button
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_str,
                            file_name=f"scraped_data_{i+1}.json",
                            mime="application/json",
                            key=f"dl_{i}"
                        )
                    with col_d2:
                        with st.popover("Plain JSON Preview"):
                            st.code(json_str, language="json")
        else:
            st.warning("No structured tables found on this page.")
            st.caption("Try a page with HTML tables (<table> tags). unstructured text extraction is coming in v2.")
