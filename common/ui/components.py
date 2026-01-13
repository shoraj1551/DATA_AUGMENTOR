"""
UI Components - Reusable Professional Components
Loading states, empty states, error handling, and more
"""
import streamlit as st


def show_loading_state(message="Loading..."):
    """Display a professional loading state"""
    st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            text-align: center;
        ">
            <div style="
                width: 40px;
                height: 40px;
                border: 3px solid var(--color-slate-200);
                border-top-color: var(--color-primary-600);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            "></div>
            <p style="color: var(--color-slate-600); font-size: 0.9rem;">
                {message}
            </p>
        </div>
        
        <style>
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
        </style>
    """, unsafe_allow_html=True)


def show_empty_state(icon="📭", title="No data yet", message="Get started by creating your first item", action_label=None, action_callback=None):
    """Display a professional empty state"""
    st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            text-align: center;
            background: var(--color-slate-50);
            border-radius: var(--radius-lg);
            border: 2px dashed var(--color-slate-300);
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">
                {icon}
            </div>
            <h3 style="
                color: var(--color-slate-900);
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">
                {title}
            </h3>
            <p style="
                color: var(--color-slate-600);
                font-size: 0.95rem;
                max-width: 400px;
                margin-bottom: 1.5rem;
            ">
                {message}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.button(action_label, on_click=action_callback, type="primary", use_container_width=True)


def show_error_state(error_message, error_details=None, show_retry=False, retry_callback=None):
    """Display a professional error state"""
    st.markdown(f"""
        <div style="
            padding: 2rem;
            background: #fee2e2;
            border-left: 4px solid var(--color-error);
            border-radius: var(--radius-md);
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="font-size: 2rem;">❌</div>
                <div style="flex: 1;">
                    <h4 style="
                        color: #991b1b;
                        font-size: 1.1rem;
                        font-weight: 600;
                        margin: 0 0 0.5rem 0;
                    ">
                        Something went wrong
                    </h4>
                    <p style="
                        color: #7f1d1d;
                        font-size: 0.9rem;
                        margin: 0;
                    ">
                        {error_message}
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if error_details:
        with st.expander("🔍 Technical Details"):
            st.code(error_details, language="text")
    
    if show_retry and retry_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.button("🔄 Try Again", on_click=retry_callback, type="primary", use_container_width=True)


def show_success_message(message, icon="✅"):
    """Display a success message"""
    st.markdown(f"""
        <div style="
            padding: 1rem 1.5rem;
            background: #d1fae5;
            border-left: 4px solid var(--color-success);
            border-radius: var(--radius-md);
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <p style="
                    color: #065f46;
                    font-size: 0.95rem;
                    font-weight: 500;
                    margin: 0;
                ">
                    {message}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def show_info_message(message, icon="ℹ️"):
    """Display an info message"""
    st.markdown(f"""
        <div style="
            padding: 1rem 1.5rem;
            background: var(--color-primary-50);
            border-left: 4px solid var(--color-primary-600);
            border-radius: var(--radius-md);
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <p style="
                    color: #1e40af;
                    font-size: 0.95rem;
                    margin: 0;
                ">
                    {message}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def show_warning_message(message, icon="⚠️"):
    """Display a warning message"""
    st.markdown(f"""
        <div style="
            padding: 1rem 1.5rem;
            background: #fef3c7;
            border-left: 4px solid var(--color-warning);
            border-radius: var(--radius-md);
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <p style="
                    color: #92400e;
                    font-size: 0.95rem;
                    font-weight: 500;
                    margin: 0;
                ">
                    {message}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_stat_card(label, value, delta=None, delta_color="normal", icon=None):
    """Render a professional stat card"""
    delta_html = ""
    if delta:
        delta_colors = {
            "normal": "var(--color-slate-600)",
            "positive": "var(--color-success)",
            "negative": "var(--color-error)",
            "off": "var(--color-slate-500)"
        }
        color = delta_colors.get(delta_color, delta_colors["normal"])
        delta_html = f'<div style="color: {color}; font-size: 0.8rem; margin-top: 0.25rem;">{delta}</div>'
    
    icon_html = f'<div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>' if icon else ""
    
    st.markdown(f"""
        <div style="
            background: #ffffff;
            padding: 1.5rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--color-slate-200);
            box-shadow: var(--shadow-sm);
        ">
            {icon_html}
            <div style="
                font-size: 0.75rem;
                font-weight: 600;
                color: var(--color-slate-600);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
            ">
                {label}
            </div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                color: var(--color-slate-900);
            ">
                {value}
            </div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def render_feature_badge(text, variant="default"):
    """Render a feature badge"""
    variants = {
        "default": ("var(--color-slate-100)", "var(--color-slate-700)"),
        "success": ("#d1fae5", "#065f46"),
        "warning": ("#fef3c7", "#92400e"),
        "error": ("#fee2e2", "#991b1b"),
        "info": ("var(--color-primary-50)", "var(--color-primary-700)")
    }
    bg, color = variants.get(variant, variants["default"])
    
    return f"""
        <span style="
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            background: {bg};
            color: {color};
            border-radius: var(--radius-full);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">
            {text}
        </span>
    """


def render_progress_bar(percentage, label=None, show_percentage=True):
    """Render a professional progress bar"""
    label_html = f'<div style="font-size: 0.85rem; color: var(--color-slate-700); margin-bottom: 0.5rem; font-weight: 500;">{label}</div>' if label else ""
    percentage_html = f'<span style="font-size: 0.85rem; color: var(--color-slate-600); font-weight: 600;">{percentage}%</span>' if show_percentage else ""
    
    st.markdown(f"""
        <div style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                {label_html}
                {percentage_html}
            </div>
            <div style="
                width: 100%;
                height: 8px;
                background: var(--color-slate-200);
                border-radius: var(--radius-full);
                overflow: hidden;
            ">
                <div style="
                    width: {percentage}%;
                    height: 100%;
                    background: linear-gradient(90deg, var(--color-primary-600), var(--color-primary-500));
                    border-radius: var(--radius-full);
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
