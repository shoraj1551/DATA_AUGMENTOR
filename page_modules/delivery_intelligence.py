"""
Delivery Intelligence page - AI-assisted execution planning
"""
import streamlit as st
import pandas as pd
import json
import altair as alt
from app_components.navigation import back_to_home
from delivery_intelligence.llm.plan_generator import generate_execution_plan
from delivery_intelligence.storage.plans_db import PlansDB
from document_parser import extractor


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
                "Upload Project Document (PRD/Spec):",
                type=['pdf', 'docx', 'txt', 'md'],
                help="Upload a document with project requirements. The AI will read it to build the plan."
            )
            prompt = st.text_area("Additional Instructions (Optional):", placeholder="E.g., Focus on the payment module first...")
            
            if uploaded_file:
                with st.spinner("Reading document..."):
                    try:
                        # Extract text using our shared extractor
                        doc_text = extractor.extract_text_from_file(uploaded_file)
                        if doc_text:
                            st.success(f"✅ Loaded {len(doc_text)} chars from {uploaded_file.name}")
                            st.session_state.plan_context = doc_text # Store for generation
                        else:
                            st.warning("Could not extract text from file.")
                    except Exception as e:
                        st.error(f"Extraction Error: {e}")
            else:
                 st.session_state.plan_context = ""
        
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
            - **Lead**: 10+ years
            """, unsafe_allow_html=True)
        
        # Team Configuration
        st.markdown("### 👥 Team Setup (Optional)")
        with st.expander("Define Team Members", expanded=False):
            st.info("Add your team members here. The AI will assign tasks based on their roles.")
            
            # Initialize session state for team if not exists
            if "team_roster" not in st.session_state:
                st.session_state.team_roster = [{"name": "Engineer 1", "role": "Full Stack", "level": "mid"}]
            
            # Simple form to add/manage team
            # We use a data editor for managing the team list easily
            team_df = pd.DataFrame(st.session_state.team_roster)
            edited_team = st.data_editor(
                team_df,
                num_rows="dynamic",
                column_config={
                    "name": "Name",
                    "role": st.column_config.SelectboxColumn(
                        "Role",
                        options=["Backend", "Frontend", "Full Stack", "Data Eng", "DevOps", "QA", "Architect"],
                        required=True
                    ),
                    "level": st.column_config.SelectboxColumn(
                        "Level",
                        options=["junior", "mid", "senior", "lead"],
                        required=True
                    )
                },
                key="team_editor"
            )
            
            # Update session state from editor
            st.session_state.team_roster = edited_team.to_dict("records")
            
            # Prepare team list with IDs for the backend
            final_team_roster = []
            for idx, member in enumerate(st.session_state.team_roster):
                if member["name"]:  # Only include if name is present
                    final_team_roster.append({
                        "id": f"eng_{idx}",
                        "name": member["name"],
                        "role": member["role"],
                        "level": member["level"]
                    })
        
        # Generate button
        if st.button("🎯 Generate Execution Plan", type="primary", use_container_width=True):
            has_context = st.session_state.get("plan_context", "")
            if (prompt and prompt.strip()) or has_context:
                with st.spinner("🤖 AI is generating your execution plan..."):
                    try:
                        # Generate plan
                        context_text = st.session_state.get("plan_context", "")
                        # If prompt is empty but we have context, use a default prompt
                        if not prompt and context_text:
                            prompt = "Generate a comprehensive execution plan based on the provided document."
                        
                        plan = generate_execution_plan(prompt, engineer_level, team_members=final_team_roster, context_text=context_text)
                        
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
    
    # TAB 2: MY PLANS & EXECUTION BOARD
    with tab2:
        # Initialize View State
        if "view_plan_id" not in st.session_state:
            st.session_state.view_plan_id = None
            
        # === DETAIL VIEW (FULL PAGE EXECUTION BOARD) ===
        if st.session_state.view_plan_id:
            plan = db.get_plan(st.session_state.view_plan_id)
            
            if not plan: 
                # Handle case where plan was deleted
                st.session_state.view_plan_id = None
                st.rerun()
            
            # Header with Back Button
            b_col1, b_col2 = st.columns([1, 5])
            with b_col1:
                if st.button("⬅️ Back", key="back_to_list"):
                    st.session_state.view_plan_id = None
                    st.rerun()
            
            with b_col2:
                st.markdown(f"### 🚀 Execution Board: {plan['title']}")
                st.caption(f"{plan['description']}")
            
            # Plan Metadata Bar
            status_colors = {"draft": "#94a3b8","pending_approval": "#f59e0b","approved": "#10b981","in_progress": "#3b82f6","completed": "#6366f1"}
            color = status_colors.get(plan['status'], "#64748b")
            st.markdown(f"""
                <div style="background-color: #f8fafc; padding: 10px 20px; border-radius: 8px; border-left: 5px solid {color}; display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                     <span style="font-weight:bold; color:{color}">{plan['status'].upper()}</span>
                     <span>📅 {plan['created_at'][:10]}</span>
                     <span>👤 {plan['engineer_level']}</span>
                     <span>⏱️ {plan.get('estimated_total_days', 0)} Days Est</span>
                     <span>📊 {calculate_progress(plan)}% Complete</span>
                </div>
            """, unsafe_allow_html=True)

            # Execution Tools
            col_tools, col_filter = st.columns([2, 1])
            with col_tools:
                # PM Controls
                if pm_mode and plan['status'] == 'pending_approval':
                    st.warning("⚠️ This plan is pending approval")
                    cols = st.columns(2)
                    if cols[0].button("✅ Approve Plan", key="app_main", type="primary"):
                        db.update_plan_status(plan['plan_id'], "in_progress")
                        st.rerun()
                    if cols[1].button("❌ Reject Plan", key="rej_main"):
                        db.update_plan_status(plan['plan_id'], "draft")
                        st.rerun()
            
            with col_filter:
                # Filter by Assignee
                assignees = set()
                for epic in plan.get('epics', []):
                    for story in epic.get('stories', []):
                        for task in story.get('tasks', []):
                            assignees.add(task.get('assignee_name', 'Unassigned'))
                
                selected_assignee = st.selectbox("👤 Filter by Assignee", ["All"] + sorted(list(assignees)), key="assignee_filter")

            st.divider()

            # RENDER EPICS AND TASKS (Full Width)
            for epic in plan.get('epics', []):
                st.markdown(f"#### 📦 {epic['title']} <span style='font-size:0.8em; color:gray'>({epic.get('estimated_days')}d)</span>", unsafe_allow_html=True)
                
                for story in epic.get('stories', []):
                    with st.container():
                        st.markdown(f"**📖 {story['title']}**")
                        # Header Row
                        h1, h2, h3, h4, h5 = st.columns([2, 4, 3, 1, 1])
                        h1.caption("Status")
                        h2.caption("Task")
                        h3.caption("Timeline & Assignee")
                        h4.caption("Hrs")
                        h5.caption("Actions")

                        for task in story.get('tasks', []):
                            # Apply filter
                            if selected_assignee != "All" and task.get('assignee_name') != selected_assignee:
                                continue
                                
                            t1, t2, t3, t4, t5 = st.columns([2, 4, 3, 1, 1])
                            
                            with t1:
                                status_options = ["not_started", "in_progress", "code_review", "unit_testing", "completed", "blocked", "verified_closed"]
                                current_status = task.get('status', 'not_started')
                                status_dot = {"not_started": "⚪", "in_progress": "🔵", "code_review": "🟡", "unit_testing": "🟠", "completed": "✅", "blocked": "🔴", "verified_closed": "🔒"}.get(current_status, "⚪")
                                
                                new_status = st.selectbox(
                                    "Status", status_options, 
                                    index=status_options.index(current_status) if current_status in status_options else 0,
                                    key=f"status_{task['task_id']}", label_visibility="collapsed",
                                    format_func=lambda x: f"{status_dot} {x.replace('_', ' ').title()}"
                                )

                            with t2:
                                st.markdown(f"{task['title']}")
                                if task.get('description'):
                                    st.caption(f"{task['description'][:50]}...")
                            
                            with t3:
                                st.caption(f"👤 `{task.get('assignee_name', 'Unassigned')}`")
                                start = task.get('start_day_offset', 1)
                                dur = task.get('duration_days', 0.5)
                                st.caption(f"📅 Day {start} - {start + dur}")
                            
                            with t4:
                                actuals = st.number_input("Hrs", value=float(task.get('actual_hours', 0)), step=0.5, key=f"act_{task['task_id']}", label_visibility="collapsed")
                            
                            with t5:
                                # Comment & PM Verify
                                comments = task.get('comments', [])
                                if st.button(f"💬 {len(comments)}", key=f"chat_{task['task_id']}"): # Popover simulation
                                     # Note: Streamlit buttons just trigger rerun, but we want popover. 
                                     # Let's use actual popover if available or expander. 
                                     # Retrying with native popover for consistency with previous step.
                                     pass 
                                
                                # Use popover for comments
                                with st.popover(f"💬 {len(comments)}"):
                                    for c in comments:
                                        st.markdown(f"**{c.get('user', 'User')}**: {c.get('text')}")
                                        st.divider()
                                    new_note = st.text_input("Add Note", key=f"note_{task['task_id']}")
                                    if new_note:
                                        # Save logic handled below via change detection
                                        # But text_input inside popover might be tricky for state. 
                                        # Reverting to direct field outside? No, let's keep inline.
                                        pass

                                if pm_mode and current_status == "completed":
                                     if st.button("🔒", key=f"lock_{task['task_id']}", help="Verify"):
                                         db.update_task_stats(plan['plan_id'], task['task_id'], {"status": "verified_closed"})
                                         st.rerun()

                            # HANDLING UPDATES SEPARATELY TO AVOID NESTING ISSUES
                            updates = {}
                            if new_status != current_status: updates["status"] = new_status
                            if actuals != task.get('actual_hours', 0): updates["actual_hours"] = actuals
                            
                            # Note input handling (Since we can't easily capture text_input inside popover and act on it immediately in loop without callback)
                            # We will use the simplified approach from before for "Add Note" but keep history in popover
                            
                            # Re-implement Note Input:
                            # notes = st.text_input("Note", key=f"inline_note_{task['task_id']}", label_visibility="collapsed", placeholder="Add note...")
                            # if notes: ... 
                            # Let's trust the previous "Add" input mechanism or just rely on the popover text input if user presses enter?
                            # Streamlit text_input updates session state on enter. 
                            
                            # Check session state for the note input key
                            note_key = f"note_{task['task_id']}"
                            if note_key in st.session_state and st.session_state[note_key]:
                                note_text = st.session_state[note_key]
                                from datetime import datetime
                                current_comments = list(task.get('comments', []))
                                current_comments.append({
                                    "user": "PM" if pm_mode else "Engineer", 
                                    "text": note_text,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                                })
                                updates["comments"] = current_comments
                                del st.session_state[note_key] # Clear
                            
                            if updates:
                                db.update_task_stats(plan['plan_id'], task['task_id'], updates)
                                st.rerun()
                                
                            st.markdown("---")


        # === MASTER VIEW (LIST OF PLANS) ===
        else:
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
                        "draft": "#94a3b8", "pending_approval": "#f59e0b",
                        "approved": "#10b981", "in_progress": "#3b82f6", "completed": "#6366f1"
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
                                        📅 {plan['created_at'][:10]} | 👤 {plan['engineer_level']}
                                    </span>
                                    <div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 10px;">
                                        <div style="flex-grow: 1; background-color: #e2e8f0; height: 6px; border-radius: 4px;">
                                            <div style="width: {progress}%; background-color: {status_color}; height: 6px; border-radius: 4px;"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_actions:
                            # Primary Action: Open Board
                            if st.button("🚀 Open Board", key=f"open_{plan['plan_id']}", use_container_width=True):
                                st.session_state.view_plan_id = plan['plan_id']
                                st.rerun()

                            # PM Quick Actions
                            if pm_mode and plan['status'] == 'pending_approval':
                                if st.button("✅ Approve", key=f"app_{plan['plan_id']}", type="primary", use_container_width=True):
                                    db.update_plan_status(plan['plan_id'], "in_progress")
                                    st.success("Approved!")
                                    st.rerun()
                            
                            if st.button("🗑️ Delete", key=f"del_{plan['plan_id']}", use_container_width=True):
                                db.delete_plan(plan['plan_id'])
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
