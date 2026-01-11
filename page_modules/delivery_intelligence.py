"""
Delivery Intelligence page - AI-assisted execution planning
"""
import streamlit as st
import pandas as pd
import json
import altair as alt
from components.navigation import back_to_home
from delivery_intelligence.llm.plan_generator import generate_execution_plan
from delivery_intelligence.storage.plans_db import PlansDB


def calculate_progress(plan):
    """Calculate progress percentage of a plan"""
    total_tasks = 0
    completed_tasks = 0
    
    for epic in plan.get('epics', []):
        for story in epic.get('stories', []):
            tasks = story.get('tasks', [])
            total_tasks += len(tasks)
            completed_tasks += len([t for t in tasks if t.get('status') == 'done'])
            
    if total_tasks == 0:
        return 0
    return int((completed_tasks / total_tasks) * 100)


def render():
    """Render the Delivery Intelligence page"""
    back_to_home("DeliveryIntelligence")
    st.markdown('<h2 class="main-header">Delivery Intelligence <span style="background:#2563eb; color:white; font-size:0.4em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-assisted execution planning for data & platform teams</p>', unsafe_allow_html=True)
    
    # Initialize database
    db = PlansDB()
    
    # Sidebar - PM Mode Toggle
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Admin Controls")
    pm_mode = st.sidebar.toggle("View as PM (Approver)", value=False)
    
    if pm_mode:
        st.sidebar.info("Signed in as: **Product Manager**")
    else:
        st.sidebar.info("Signed in as: **Engineer**")
    
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
                                        is_done = task['status'] == 'done'
                                        status_icon = "✅" if is_done else "⬜"
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
                progress = calculate_progress(plan)
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
                                <div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 10px;">
                                    <div style="flex-grow: 1; background-color: #e2e8f0; height: 8px; border-radius: 4px;">
                                        <div style="width: {progress}%; background-color: {status_color}; height: 8px; border-radius: 4px;"></div>
                                    </div>
                                    <span style="font-size: 0.75rem; color: #64748b; font-weight: 600;">{progress}%</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_actions:
                        # PM Approval Workflow
                        if pm_mode and plan['status'] == 'pending_approval':
                            if st.button("✅ Approve", key=f"app_{plan['plan_id']}", type="primary"):
                                db.update_plan_status(plan['plan_id'], "in_progress")
                                st.success(f"Plan '{plan['title']}' approved!")
                                st.rerun()
                                
                            if st.button("❌ Reject", key=f"rej_{plan['plan_id']}"):
                                db.update_plan_status(plan['plan_id'], "draft")
                                st.warning(f"Plan '{plan['title']}' rejected (sent back to draft).")
                                st.rerun()

                        # View / Edit Details and Task Management
                        with st.expander("Show Details & Tasks"):
                             for epic in plan.get('epics', []):
                                st.markdown(f"**{epic['title']}**")
                                for story in epic.get('stories', []):
                                    st.markdown(f"&nbsp;&nbsp;*Story: {story['title']}*")
                                    for task in story.get('tasks', []):
                                        # Task checkbox (Interactive only if In Progress)
                                        task_key = f"task_{task['task_id']}"
                                        is_completed = task['status'] == 'done'
                                        
                                        # Only allow checking if plan is in progress
                                        disabled = plan['status'] != 'in_progress'
                                        
                                        new_status = st.checkbox(
                                            f"{task['title']} ({task.get('estimated_hours',0)}h)", 
                                            value=is_completed, 
                                            key=task_key,
                                            disabled=disabled
                                        )
                                        
                                        # Handle status change
                                        if not disabled and new_status != is_completed:
                                            # Update task status in memory plan object
                                            task['status'] = 'done' if new_status else 'todo'
                                            # Save updated plan to DB
                                            db.save_plan(plan)
                                            st.rerun()
        else:
            st.info("No plans found. Create your first plan in the 'Create Plan' tab!")
    
    # TAB 3: DASHBOARD
    with tab3:
        st.subheader("Analytics Dashboard")
        
        all_plans = db.get_all_plans()
        
        if all_plans:
            # 1. High-level Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Plans", len(all_plans))
            
            with col2:
                pending = len([p for p in all_plans if p['status'] == 'pending_approval'])
                st.metric("Pending Approval", pending, delta=pending if pending > 0 else None, delta_color="off")
            
            with col3:
                active = len([p for p in all_plans if p['status'] == 'in_progress'])
                st.metric("Active Plans", active, delta=active if active > 0 else None)
            
            with col4:
                # Estimate 4 hours saved per plan vs manual planning
                hours_saved = len(all_plans) * 4
                st.metric("Est. Time Saved", f"{hours_saved}h", help="Assuming 4h manual planning saved per plan")
            
            st.markdown("---")
            
            # 2. Charts Row
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("### 📊 Plan Status")
                status_counts = {}
                for plan in all_plans:
                    status = plan['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                
                # Altair Donut Chart for Status
                base = alt.Chart(df_status).encode(
                    theta=alt.Theta("Count", stack=True)
                )
                pie = base.mark_arc(outerRadius=120, innerRadius=60).encode(
                    color=alt.Color("Status", scale=alt.Scale(scheme='category20')),
                    order=alt.Order("Count", sort="descending"),
                    tooltip=["Status", "Count"]
                )
                text = base.mark_text(radius=140).encode(
                    text="Count",
                    order=alt.Order("Count", sort="descending"),
                    color=alt.value("black")
                )
                st.altair_chart(pie + text, use_container_width=True)

            with chart_col2:
                st.markdown("### 👥 Engineer Distribution")
                level_counts = {}
                for plan in all_plans:
                    lvl = plan.get('engineer_level', 'unknown')
                    level_counts[lvl] = level_counts.get(lvl, 0) + 1
                
                df_levels = pd.DataFrame(list(level_counts.items()), columns=['Level', 'Count'])
                
                bar_chart = alt.Chart(df_levels).mark_bar().encode(
                    x=alt.X('Level', sort=['junior', 'mid', 'senior', 'lead']),
                    y='Count',
                    color=alt.Color('Level', legend=None),
                    tooltip=['Level', 'Count']
                )
                st.altair_chart(bar_chart, use_container_width=True)

            # 3. Active Plans Progress
            st.markdown("### 🚀 Active Plans Progress")
            active_plans_data = []
            for plan in all_plans:
                if plan['status'] in ['in_progress', 'pending_approval']:
                    progress = calculate_progress(plan)
                    active_plans_data.append({
                        "Plan": plan['title'],
                        "Progress": progress,
                        "Status": plan['status']
                    })
            
            if active_plans_data:
                df_active = pd.DataFrame(active_plans_data)
                
                progress_chart = alt.Chart(df_active).mark_bar().encode(
                    x=alt.X('Progress', scale=alt.Scale(domain=[0, 100]), title='Completion (%)'),
                    y=alt.Y('Plan', sort='-x'),
                    color=alt.Color('Status', scale=alt.Scale(range=['#3b82f6', '#f59e0b'])),
                    tooltip=['Plan', 'Progress', 'Status']
                ).properties(height=max(100, len(df_active) * 40))
                
                text_chart = progress_chart.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text=alt.Text('Progress', format='d')
                )
                
                st.altair_chart(progress_chart + text_chart, use_container_width=True)
            else:
                st.info("No active plans to show progress for.")

        else:
            st.info("No data available yet. Create your first plan to see analytics!")
