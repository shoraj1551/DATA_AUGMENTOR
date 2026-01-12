"""
Web Data Scraper Page Module
"""
import streamlit as st
import pandas as pd
import json
from app_components.navigation import back_to_home
from web_scraper import validator, fetcher, parser

def render():
    """Render the Web Data Scraper page"""
    back_to_home("WebScraper")
    st.markdown('<h2 class="main-header">Web Data Scraper <span style="background:#2563eb; color:white; font-size:0.4em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract structured data from web pages compliant with robots.txt</p>', unsafe_allow_html=True)
    
    # Initialize session state for URL
    if "scraper_url" not in st.session_state:
        st.session_state.scraper_url = ""

    # --- AI Source Suggestion (Optional) ---
    with st.expander("🤖 Don't know where to look? Ask AI for a source", expanded=True):
        col_ai1, col_ai2 = st.columns([3, 1])
        with col_ai1:
            requirements = st.text_input("Describe the data you need:", placeholder="e.g., List of S&P 500 companies with tickers")
        with col_ai2:
            st.write("")
            st.write("")
            suggest_btn = st.button("✨ Suggest Source", type="secondary")
        
        # Initialize suggestions if not present
        if "ai_suggestions" not in st.session_state:
            st.session_state.ai_suggestions = []

        if suggest_btn and requirements:
            with st.spinner("AI is researching top sources & checking permissions..."):
                from web_scraper import ai_extractor
                st.session_state.ai_suggestions = ai_extractor.suggest_website_source(requirements)
        
        # Render from Session State
        suggestions = st.session_state.ai_suggestions
        if suggestions:
            # Filter out empty URLs just in case
            valid_suggestions = [s for s in suggestions if s.get("url")]
            
            if valid_suggestions:
                expander_title = f"🔍 AI Suggestions ({len(valid_suggestions)})"
                
                for idx, item in enumerate(valid_suggestions):
                    with st.container():
                        # Header with Badge
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**{idx+1}. [{item['url']}]({item['url']})**")
                        with c2:
                            if item['is_allowed']:
                                st.markdown('<span style="background:#dcfce7; color:#166534; padding:2px 8px; border-radius:12px; font-size:0.8em;">Allowed</span>', unsafe_allow_html=True)
                            else:
                                st.markdown('<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:12px; font-size:0.8em;">Blocked</span>', unsafe_allow_html=True)
                        
                        # Set description and tips
                        st.caption(f"Reason: {item['reason']}")
                        if item.get("access_tips"):
                            st.info(f"💡 **Access Tip**: {item['access_tips']}")
                        
                        # Use button
                        if st.button("📋 Use this Source", key=f"use_{idx}"):
                             st.session_state.scraper_url = item['url']
                             st.rerun() # Rerun to update the input field immediately
                        
                        st.divider()
            else:
                if suggest_btn: # Only show error if just clicked
                    st.warning("AI returned a response but no valid URLs were found.")

    # Input Section
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            url = st.text_input("Enter Website URL:", key="scraper_url", placeholder="https://example.com/data")
            
            # Example Button
            def set_example():
                st.session_state.scraper_url = "http://books.toscrape.com/"
            
            st.button("📚 Try Example: Books To Scrape", on_click=set_example, type="secondary", help="Click to load a safe scraping sandbox")

        with col2:
            st.write("") # Spacer
            st.write("")
            scrape_btn = st.button("🚀 Check & Scrape", type="primary", use_container_width=True)
    
    # Initialize force_scrape state
    if "force_scrape" not in st.session_state:
        st.session_state.force_scrape = False

    # Reset force_scrape if new scrape initiated
    if scrape_btn:
        st.session_state.force_scrape = False

    # Process if Scrape Button click OR Force Scrape is active
    if (scrape_btn or st.session_state.force_scrape) and url:
        if not url.startswith("http"):
            st.error("Please enter a valid URL starting with http:// or https://")
            return

        with st.status("Processing...", expanded=True) as status:
            # 1. Compliance Check
            st.write("🔍 Checking robots.txt compliance...")
            is_allowed = validator.is_scraping_allowed(url)
            
            if not is_allowed:
                if st.session_state.force_scrape:
                    st.warning("⚠️ Bypassing robots.txt restrictions as requested.")
                else:
                    status.update(label="Scraping Disallowed", state="error")
                    st.error(f"🛑 Scraping is disallowed by the website's robots.txt policy for this URL.")
                    st.info("We respect website policies, but you can override this manually.")
                    
                    if st.button("⚠️ Bypass & Scrape Anyway", type="primary"):
                        st.session_state.force_scrape = True
                        st.rerun()
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
