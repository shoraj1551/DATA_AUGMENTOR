"""
Delivery Intelligence page - AI-assisted execution planning
"""
import streamlit as st
import pandas as pd
import json
from components.navigation import back_to_home
from delivery_intelligence.llm.plan_generator import generate_execution_plan
from delivery_intelligence.storage.plans_db import PlansDB


def render():
    """Render the Delivery Intelligence page"""
    back_to_home("DeliveryIntelligence")
    st.markdown('<h2 class="main-header">Delivery Intelligence</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-assisted execution planning for data & platform teams</p>', unsafe_allow_html=True)
    
    # Initialize database
    db = PlansDB()
    
    # Tab navigation
    tab1, tab2, tab3 = st.tabs(["📝 Create Plan", "📋 My Plans", "📊 Dashboard"])
    
    # TAB 1: CREATE PLAN
    with tab1:
        st.subheader("Generate Execution Plan")
        
        # Input method selection
        input_method = st.radio(
            "Input Method:",
            ["Text Prompt", "Upload Document"],
            horizontal=True
        )
        
        if input_method == "Text Prompt":
            prompt = st.text_area(
                "Describe your project or feature:",
                placeholder="E.g., Build a real-time data pipeline to ingest customer events from Kafka, transform them using Spark, and load into Snowflake for analytics...",
                height=150
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload project document:",
                type=['pdf', 'docx', 'txt'],
                help="Upload a document with project requirements"
            )
            prompt = None
            if uploaded_file:
                st.info("📄 Document uploaded. Extraction coming in Phase 5!")
                prompt = f"[Document: {uploaded_file.name}] - Document parsing will be implemented in Phase 5"
        
        # Engineer experience level
        col1, col2 = st.columns([2, 1])
        
        with col1:
            engineer_level = st.selectbox(
                "Engineer Experience Level:",
                ["junior", "mid", "senior", "lead"],
                index=1,
                help="Timeline estimates will be adjusted based on experience level"
            )
        
        with col2:
            st.markdown("### Experience Guide")
            st.markdown("""
            - **Junior**: 0-2 years
            - **Mid**: 2-5 years
            - **Senior**: 5-10 years
            - **Lead**: 10+ years
            """, unsafe_allow_html=True)
        
        # Generate button
        if st.button("🎯 Generate Execution Plan", type="primary", use_container_width=True):
            if prompt and prompt.strip():
                with st.spinner("🤖 AI is generating your execution plan..."):
                    try:
                        # Generate plan
                        plan = generate_execution_plan(prompt, engineer_level)
                        
                        # Save to database
                        plan_id = db.save_plan(plan)
                        
                        st.success(f"✅ Plan generated successfully! Plan ID: `{plan_id[:8]}...`")
                        
                        # Display generated plan
                        st.markdown("---")
                        st.markdown(f"### {plan['title']}")
                        st.markdown(f"*{plan['description']}*")
                        st.markdown(f"**Status:** `{plan['status']}` | **Engineer Level:** `{plan['engineer_level']}` | **Total Est:** `{plan.get('estimated_total_days', 0)} Days`")
                        
                        # Display epics, stories, and tasks
                        for epic in plan['epics']:
                            epic_est = epic.get('estimated_days', 0)
                            with st.expander(f"📦 **Epic:** {epic['title']} (Est: {epic_est} days)", expanded=True):
                                st.markdown(f"*{epic['description']}*")
                                
                                for story in epic['stories']:
                                    story_est = story.get('estimated_hours', 0)
                                    st.markdown(f"#### 📖 Story: {story['title']} <span style='background:#e2e8f0; color:#475569; padding:2px 8px; border-radius:12px; font-size:0.8em'>sc {story_est}h</span>", unsafe_allow_html=True)
                                    st.markdown(f"*{story['description']}*")
                                    
                                    if story.get('acceptance_criteria'):
                                        st.markdown("**Acceptance Criteria:**")
                                        for criterion in story['acceptance_criteria']:
                                            st.markdown(f"- ✓ {criterion}")
                                    
                                    st.markdown("**Tasks:**")
                                    for task in story['tasks']:
                                        status_icon = "⬜" if task['status'] == "todo" else "✅"
                                        task_est = task.get('estimated_hours', 0)
                                        st.markdown(f"{status_icon} {task['title']} *({task_est}h)*")
                                    
                                    st.markdown("---")
                        
                        # Action buttons
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("📥 Download as JSON", key="download_json"):
                                json_str = json.dumps(plan, indent=2)
                                st.download_button(
                                    "💾 Save JSON",
                                    json_str,
                                    f"plan_{plan_id[:8]}.json",
                                    "application/json"
                                )
                        with col_b:
                            if st.button("✏️ Edit Plan", key="edit_plan"):
                                st.info("Edit functionality coming in Phase 3!")
                        with col_c:
                            if st.button("✅ Submit for Approval", key="submit_approval"):
                                db.update_plan_status(plan_id, "pending_approval")
                                st.success("Plan submitted for PM approval!")
                                st.rerun()
                    
                    except Exception as e:
                        import traceback
                        st.error(f"Error generating plan: {str(e)}")
                        st.error(f"Details: {traceback.format_exc()}")
            else:
                st.warning("Please provide a project description or upload a document.")
    
    # TAB 2: MY PLANS
    with tab2:
        st.subheader("All Execution Plans")
        
        # Filters
        col1, col2 = st.columns([1, 3])
        with col1:
            status_filter = st.selectbox(
                "Filter by Status:",
                ["All", "draft", "pending_approval", "approved", "in_progress", "completed"]
            )
        
        # Get plans
        if status_filter == "All":
            plans = db.get_all_plans()
        else:
            plans = db.get_plans_by_status(status_filter)
        
        if plans:
            st.markdown(f"**Found {len(plans)} plan(s)**")
            
            for plan in reversed(plans):  # Show newest first
                # Status badge color
                status_colors = {
                    "draft": "#94a3b8",
                    "pending_approval": "#f59e0b",
                    "approved": "#10b981",
                    "in_progress": "#3b82f6",
                    "completed": "#6366f1"
                }
                status_color = status_colors.get(plan['status'], "#64748b")
                
                with st.container():
                    col_info, col_actions = st.columns([4, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        <div style="padding: 1rem; border-left: 4px solid {status_color}; background: #f8fafc; border-radius: 8px; margin-bottom: 1rem;">
                            <h4 style="margin: 0 0 0.5rem 0;">{plan['title']}</h4>
                            <p style="margin: 0; color: #64748b; font-size: 0.9rem;">{plan['description'][:100]}...</p>
                            <div style="margin-top: 0.5rem;">
                                <span style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                    {plan['status'].upper()}
                                </span>
                                <span style="margin-left: 1rem; color: #64748b; font-size: 0.85rem;">
                                    📅 {plan['created_at'][:10]} | 👤 {plan['engineer_level']} | ⏱️ {plan.get('estimated_total_days', 0)} Days
                                    </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_actions:
                        if st.button("View", key=f"view_{plan['plan_id']}"):
                            st.session_state.selected_plan = plan['plan_id']
                            st.info(f"Plan details view coming in Phase 4! Plan ID: {plan['plan_id'][:8]}")
        else:
            st.info("No plans found. Create your first plan in the 'Create Plan' tab!")
    
    # TAB 3: DASHBOARD
    with tab3:
        st.subheader("Analytics Dashboard")
        
        all_plans = db.get_all_plans()
        
        if all_plans:
            # Stats cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Plans", len(all_plans))
            
            with col2:
                pending = len([p for p in all_plans if p['status'] == 'pending_approval'])
                st.metric("Pending Approval", pending)
            
            with col3:
                active = len([p for p in all_plans if p['status'] == 'in_progress'])
                st.metric("Active Plans", active)
            
            with col4:
                completed = len([p for p in all_plans if p['status'] == 'completed'])
                st.metric("Completed", completed)
            
            # Status distribution
            st.markdown("### Status Distribution")
            status_counts = {}
            for plan in all_plans:
                status = plan['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            st.bar_chart(df_status.set_index('Status'))
            
            # Recent activity
            st.markdown("### Recent Plans")
            recent_plans = sorted(all_plans, key=lambda x: x['created_at'], reverse=True)[:5]
            
            for plan in recent_plans:
                st.markdown(f"- **{plan['title']}** - `{plan['status']}` - {plan['created_at'][:10]}")
        else:
            st.info("No data available yet. Create your first plan to see analytics!")
