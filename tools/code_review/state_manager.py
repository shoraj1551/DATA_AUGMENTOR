import streamlit as st
from typing import Optional, List, Dict, Any

class CodeReviewStateManager:
    """
    Centralized state manager for the Code Review tool.
    Prevents race conditions and "stale state" by encapsulating session_state access.
    """
    
    # Define keys to manage
    KEYS = {
        'original_code': str,
        'original_filename': str,
        'language': str,
        'review_report': str,
        'failure_scenarios': list,
        'unit_tests': str,
        'functional_tests': str,
        'analysis_complete': bool,
        'documented_code': str,
        'fixed_code': str,
        'fix_details': list,
        'docs_accepted': bool,
        'fixed_accepted': bool,
        'use_documented_for_fix': bool,
        'last_uploaded_filename': str
    }

    @staticmethod
    def initialize():
        """Ensure all keys exist with default values if not present."""
        defaults = {
            'review_report': "",
            'failure_scenarios': [],
            'analysis_complete': False,
            'fix_details': [],
            'unit_tests': "",
            'functional_tests': "",
            'documented_code': None,
            'fixed_code': None,
            'docs_accepted': False,
            'fixed_accepted': False,
            'use_documented_for_fix': False
        }
        
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @staticmethod
    def reset_analysis():
        """Clear all analysis/solution results but keep uploaded file info."""
        keys_to_clear = [
            'review_report', 'failure_scenarios', 'unit_tests', 'functional_tests',
            'analysis_complete', 'documented_code', 'fixed_code', 
            'docs_accepted', 'fixed_accepted', 'use_documented_for_fix', 
            'fix_details'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Re-init defaults immediately to prevent KeyErrors
        CodeReviewStateManager.initialize()

    @staticmethod
    def set_new_file(filename: str, code: str, language: str):
        """Register a new file and fully reset the state."""
        CodeReviewStateManager.reset_analysis()
        st.session_state.original_filename = filename
        st.session_state.original_code = code
        st.session_state.language = language
        st.session_state.last_uploaded_filename = filename
        st.session_state.analysis_complete = False

    @staticmethod
    def mark_analysis_complete():
        """Signal that analysis is done and solutions can be shown."""
        st.session_state.analysis_complete = True

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Safe getter for session state."""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """Safe setter."""
        st.session_state[key] = value
