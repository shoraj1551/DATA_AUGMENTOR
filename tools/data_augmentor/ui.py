"""
DataAugmentor page - Generate, augment, and secure data
"""
import streamlit as st
import pandas as pd
from common.ui.navigation import back_to_home
from llm.generate_synthetic_data import generate_synthetic_data
from llm.augment_existing_data import augment_existing_data
from tools.data_augmentor.pii_masking import mask_pii_data
from llm.generate_edge_case_data import generate_edge_case_data


def render():
    """Render the DataAugmentor page"""
    back_to_home("DataAugmentor")
    st.markdown('<h2 class="main-header">DataAugmentor</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Generate, augment, and secure your data</p>', unsafe_allow_html=True)
    
    operation = st.selectbox(
        "Select Operation:",
        ["Generate Synthetic Data", "Augment Existing Data", "Mask PII Data", "Generate Edge Case Data"]
    )
    
    if operation == "Generate Synthetic Data":
        st.subheader("Generate Synthetic Data")
        
        # Initialize session state for retry
        if 'last_synthetic_prompt' not in st.session_state:
            st.session_state.last_synthetic_prompt = ""
        if 'last_synthetic_rows' not in st.session_state:
            st.session_state.last_synthetic_rows = 10
        if 'synthetic_result' not in st.session_state:
            st.session_state.synthetic_result = None
        
        prompt = st.text_area("Describe the data you want:", 
                             value=st.session_state.last_synthetic_prompt,
                             placeholder="E.g., Customer data with name, email, age, and city",
                             height=100)
        num_rows = st.slider("Number of rows:", 1, 1000, st.session_state.last_synthetic_rows)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            generate_clicked = st.button("Generate Data", use_container_width=True)
        
        with col2:
            retry_clicked = st.button("🔄 Retry (New Data)", use_container_width=True)
        
        if generate_clicked or retry_clicked:
            if prompt:
                # Store for retry
                st.session_state.last_synthetic_prompt = prompt
                st.session_state.last_synthetic_rows = num_rows
                
                with st.spinner("Generating synthetic data..."):
                    try:
                        # For retry, add timestamp to bypass cache and get fresh data
                        import time
                        if retry_clicked:
                            actual_prompt = f"{prompt}\\n\\n[Variation {int(time.time())}]"
                        else:
                            actual_prompt = prompt
                        
                        df = generate_synthetic_data(actual_prompt, num_rows)
                        st.session_state.synthetic_result = df
                        st.success(f"✅ Generated {len(df)} rows!")
                        st.dataframe(df)
                        
                        csv = df.to_csv(index=False)
                        st.download_button("📥 Download CSV", csv, "synthetic_data.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.synthetic_result = None
            else:
                st.warning("Please describe the data you want to generate.")
    
    elif operation == "Augment Existing Data":
        st.subheader("Augment Existing Data")
        
        uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("**Original Data:**")
            st.dataframe(df.head())
            
            prompt = st.text_area("Additional requirements (optional):", height=80)
            num_rows = st.slider("Number of rows to add:", 1, 100, 5)
            
            if st.button("Augment Data"):
                with st.spinner("Augmenting data..."):
                    try:
                        augmented_df = augment_existing_data(df, prompt, num_rows)
                        st.success(f"✅ Added {num_rows} rows!")
                        st.dataframe(augmented_df.tail(num_rows))
                        
                        csv = augmented_df.to_csv(index=False)
                        st.download_button("📥 Download Augmented CSV", csv, "augmented_data.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    elif operation == "Mask PII Data":
        st.subheader("Mask PII Data")
        
        uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("**Original Data:**")
            st.dataframe(df.head())
            
            # Step 1: Identify PII Columns
            st.markdown("### Step 1: Identify PII Columns")
            pii_patterns = ['name', 'email', 'phone', 'address', 'ssn', 'social', 'dob', 'birth']
            suggested_pii_cols = [col for col in df.columns if any(pattern in col.lower() for pattern in pii_patterns)]
            
            selected_pii_cols = st.multiselect(
                "Select columns to MASK (you can add/remove columns):",
                options=df.columns,
                default=suggested_pii_cols,
                help="The AI will attempt to find PII columns, but you can manually select the correct ones here."
            )
            
            # Calculate exclude_cols -> All columns NOT selected
            exclude_cols = [col for col in df.columns if col not in selected_pii_cols]

            if selected_pii_cols:
                # Step 2: Configure Rules
                st.markdown("### Step 2: Configure Rules")
                
                default_rules = """- Age: Replace with random ages (e.g., 25, 42, 38)
- Income: Replace with masked values (e.g., "XXXXX", "MASKED", or random numbers)
- Names: Replace with "Person_1", "Person_2", etc.
- Emails: Replace with "user1@example.com", "user2@example.com"
- Phone: Replace with "XXX-XXX-XXXX"
- Addresses: Replace with "123 Main St", "456 Oak Ave" """

                with st.expander("⚙️ Customize Masking Logic", expanded=False):
                    masking_rules = st.text_area(
                        "Edit Masking Rules (Instructions for AI):",
                        value=default_rules,
                        height=150,
                        help="Analyze the rules above and modify them to control how specific PII is masked."
                    )
                
                # Step 3: Action
                st.markdown("### Step 3: Mask & Download")
                if st.button("🎭 Mask PII Data", type="primary"):
                    with st.spinner("Masking PII data..."):
                        try:
                            masked_df = mask_pii_data(df, exclude_cols, masking_rules)
                            st.success("✅ PII data masked successfully!")
                            
                            st.write("**Preview (Top 5 Rows):**")
                            st.dataframe(masked_df.head())
                            
                            csv = masked_df.to_csv(index=False)
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.download_button(
                                    "📥 Download Masked CSV", 
                                    csv, 
                                    "masked_data.csv", 
                                    "text/csv",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.info("Please select at least one column to mask.")
    
    elif operation == "Generate Edge Case Data":
        st.subheader("Generate Edge Case Data")
        
        uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("**Original Data:**")
            st.dataframe(df.head())
            
            prompt = st.text_area("Describe edge cases (optional):", height=80)
            num_rows = st.slider("Number of edge cases:", 1, 50, 5)
            
            if st.button("Generate Edge Cases"):
                with st.spinner("Generating edge cases..."):
                    try:
                        edge_df = generate_edge_case_data(df, prompt, num_rows)
                        st.success(f"✅ Generated {num_rows} edge cases!")
                        st.dataframe(edge_df)
                        
                        csv = edge_df.to_csv(index=False)
                        st.download_button("📥 Download Edge Cases CSV", csv, "edge_cases.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
