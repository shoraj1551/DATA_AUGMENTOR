"""
Delivery Intelligence page - AI-assisted execution planning
"""
import streamlit as st
import pandas as pd
import json
import altair as alt
from common.ui.navigation import render_page_header
from tools.delivery_intelligence.llm.plan_generator import generate_execution_plan
from tools.delivery_intelligence.storage.plans_db import PlansDB
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
    render_page_header(
        title="Delivery Intelligence",
        subtitle="AI-assisted execution planning for data & platform teams",
        icon="🎯",
        status="beta"
    )
    
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
        st.markdown("### 👥 Team Setup (Required)")
        st.info("Define your team structure. The AI needs at least one member to assign tasks.")
        
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
                "name": st.column_config.TextColumn("Name", required=True),
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
            if member.get("name"):  # Only include if name is present
                final_team_roster.append({
                    "id": f"eng_{idx}",
                    "name": member.get("name"),
                    "role": member.get("role", "Full Stack"),
                    "level": member.get("level", "mid")
                })
        
        # Generate button
        if st.button("🎯 Generate Execution Plan", type="primary", use_container_width=True):
            has_context = st.session_state.get("plan_context", "")
            
            # Validation
            if not final_team_roster:
                st.error("⚠️ Team cannot be empty. Please add at least one team member.")
            elif not ((prompt and prompt.strip()) or has_context):
                st.warning("Please provide a project description or upload a document.")
            else:
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
                # Top Header
                c_title, c_stats = st.columns([3, 2])
                with c_title:
                    st.markdown(f"### 🚀 {plan['title']}")
                with c_stats:
                    progress = calculate_progress(plan)
                    st.progress(progress/100, text=f"Overall Progress: {progress}%")
            
            # Sub-Navigation for the Board
            board_view = st.radio("View Mode:", ["📊 Dashboard", "📋 List & Tasks", "📅 Timeline (Gantt)", "📌 Sticky Board", "📚 Project Knowledge"], horizontal=True, label_visibility="collapsed")
            st.divider()

            # =========================================================
            # VIEW 0: DASHBOARD (Added)
            # =========================================================
            if board_view == "📊 Dashboard":
                from tools.delivery_intelligence.llm.advisor import PlanAdvisor
                
                # --- Metrics Calculation ---
                all_tasks = []
                for epic in plan.get('epics', []):
                    for story in epic.get('stories', []):
                        for task in story.get('tasks', []):
                            all_tasks.append(task)
                
                total_tasks = len(all_tasks)
                completed_tasks = len([t for t in all_tasks if t['status'] in ['completed', 'verified_closed']])
                blocked_tasks = len([t for t in all_tasks if t['status'] == 'blocked'])
                in_progress_tasks = len([t for t in all_tasks if t['status'] in ['in_progress', 'code_review', 'unit_testing']])
                
                completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
                
                # --- 1. HEADLINE STATS ---
                st.markdown(f"### 🚦 Project Pulse: {plan['title']}")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Progress", f"{completion_rate}%", delta_color="normal")
                m2.metric("Tasks Done", f"{completed_tasks}/{total_tasks}")
                m3.metric("In Flight", in_progress_tasks, delta_color="off")
                m4.metric("Blockers", blocked_tasks, delta="-"+str(blocked_tasks) if blocked_tasks > 0 else "0", delta_color="inverse")
                
                st.divider()
                
                # --- 2. TEAM & WORKLOAD ---
                c1, c2 = st.columns([3, 2])
                
                with c1:
                    st.subheader("👥 Team Workload")
                    
                    # Team Stats Logic
                    team_stats = {}
                    for t in all_tasks:
                        assignee = t.get('assignee_name', 'Unassigned')
                        if assignee not in team_stats:
                            team_stats[assignee] = {"Total": 0, "Done": 0, "Active": 0, "Blocked": 0}
                        
                        stats = team_stats[assignee]
                        stats["Total"] += 1
                        if t['status'] in ['completed', 'verified_closed']:
                            stats["Done"] += 1
                        elif t['status'] == 'blocked':
                            stats["Blocked"] += 1
                        elif t['status'] != 'not_started':
                            stats["Active"] += 1
                    
                    # Create DataFrame
                    if team_stats:
                        rows = []
                        for user, data in team_stats.items():
                            rows.append({
                                "Member": user,
                                "Tasks": data['Total'],
                                "Active 🔵": data['Active'],
                                "Done ✅": data['Done'],
                                "Blocked 🔴": data['Blocked'], 
                                "Capacity": "⚠️ Overloaded" if data['Active'] > 4 else "🟢 Good"
                            })
                        
                        st.dataframe(
                            pd.DataFrame(rows),
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Capacity": st.column_config.TextColumn(
                                    "Status",
                                    help="Active > 4 considers overloaded",
                                    width="small"
                                )
                            }
                        )
                    else:
                        st.info("No tasks assigned yet.")

                with c2:
                    st.subheader("📊 Task Velocity")
                    if total_tasks > 0:
                        # Pie Chart for Status
                        status_counts = {}
                        for t in all_tasks:
                            s = t.get('status', 'not_started')
                            status_counts[s] = status_counts.get(s, 0) + 1
                        
                        df_status = pd.DataFrame([{"Status": k, "Count": v} for k, v in status_counts.items()])
                        
                        chart = alt.Chart(df_status).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta("Count", stack=True),
                            color=alt.Color("Status", scale=alt.Scale(scheme="category20b")),
                            tooltip=["Status", "Count"]
                        )
                        st.altair_chart(chart, use_container_width=True)
                
                # --- 3. ISSUES HUB ---
                st.divider()
                st.subheader("🚨 Issue Hub & AI Alerts")
                
                # Get AI Alerts
                advisor = PlanAdvisor()
                alerts = advisor.analyze_plan_health(plan)
                
                col_issues, col_risk_map = st.columns([3, 1])
                
                with col_issues:
                    if not alerts and blocked_tasks == 0:
                        st.success("🎉 No blocks or risks detected! Smooth sailing.")
                    else:
                        # 1. Show Blocked Tasks first
                        if blocked_tasks > 0:
                            st.markdown("#### 🚫 Active Blockers")
                            for t in all_tasks:
                                if t['status'] == 'blocked':
                                    st.error(f"**{t['title']}** ({t.get('assignee_name')}) - Marked as BLOCKED")
                        
                        # 2. Show AI Alerts
                        if alerts:
                            st.markdown("#### 🤖 AI Detected Risks")
                            for alert in alerts:
                                color = "red" if alert['type'] == 'danger' else "orange"
                                st.markdown(f":{color}[**{alert['type'].upper()}**: {alert['message']}]")
                
                with col_risk_map:
                    if st.button("🧠 Refresh Analysis"):
                        st.rerun()
                    st.caption("AI analyzes comments, dates, and status patterns to find hidden risks.")
            
            # =========================================================
            # VIEW D: PROJECT KNOWLEDGE (Added)
            # =========================================================
            elif board_view == "📚 Project Knowledge":
                st.subheader("Project Knowledge Repository")
                st.caption(f"All assets, docs, and notes linked to '{plan['title']}'")
                
                if 'kb_ingestor' not in st.session_state:
                     from tools.knowledge_base.ingestor import ContentIngestor
                     st.session_state.kb_ingestor = ContentIngestor()
                
                ingestor = st.session_state.kb_ingestor
                
                # Fetch entries for this project
                project_tag = f"project:{plan['plan_id']}"
                entries = ingestor.search_entries(tags=[project_tag])
                
                # Layout: Left = Search/List, Right = Add New
                k_col1, k_col2 = st.columns([2, 1])
                
                with k_col1:
                    st.markdown(f"**📂 Repository ({len(entries)} items)**")
                    k_search = st.text_input("🔍 Search within project...", key="proj_kb_search")
                    
                    if k_search:
                        # Client-side filter since we already fetched project specific ones
                        entries = [e for e in entries if k_search.lower() in e['content'].lower() or k_search.lower() in str(e.get('tags', '')).lower()]
                    
                    if not entries:
                        st.info("No documents found. Add some on the right!")
                    
                    for e in entries:
                        with st.expander(f"📄 {e['category'].upper()} - {e['content'][:40]}..."):
                            st.markdown(e['content'])
                            st.caption(f"🏷️ Tags: {', '.join(e.get('tags', []))}")
                            st.caption(f"📅 {e['created_at']}")
                            
                            # Link to task if present
                            for t in e.get('tags', []):
                                if t.startswith("task:"):
                                    tid = t.split(":")[1]
                                    st.caption(f"🔗 Linked to Task ID: {tid}")
                
                with k_col2:
                    with st.container(border=True):
                        st.markdown("### ➕ Add Knowledge")
                        new_k_content = st.text_area("Content / Link / Code", height=150, key="new_pk_content")
                        new_k_cat = st.selectbox("Category", ["documentation", "decision", "meeting_note", "code", "other"], key="new_pk_cat")
                        new_k_tags = st.text_input("Additional Tags (comma sep)", key="new_pk_tags")
                        
                        if st.button("💾 Save to Project", key="save_pk_main", type="primary"):
                            if new_k_content:
                                final_tags = [project_tag]
                                if new_k_tags:
                                    final_tags.extend([t.strip() for t in new_k_tags.split(",") if t.strip()])
                                
                                ingestor.add_entry(
                                    content=new_k_content,
                                    category=new_k_cat,
                                    tags=final_tags,
                                    metadata={"author": "PM" if pm_mode else "Eng", "source": "Delivery Board"}
                                )
                                st.success("Added!")
                                st.rerun()
                            else:
                                st.error("Content required")
            # =========================================================
            # VIEW A: LIST & TASKS (Enhanced)
            # =========================================================
            if board_view == "📋 List & Tasks":
                
                # --- AI ADVISOR PANEL ---
                from tools.delivery_intelligence.llm.advisor import PlanAdvisor
                advisor = PlanAdvisor()
                alerts = advisor.analyze_plan_health(plan)
                
                if alerts:
                    with st.expander("🤖 AI Project Advisor Alerts", expanded=True):
                        for alert in alerts:
                            color = "red" if alert['type'] == 'danger' else "orange"
                            st.markdown(f":{color}[{alert['message']}]")
                        
                        if st.button("🧠 Generate Detailed Analysis"):
                            with st.spinner("Analyzing project health..."):
                                advice = advisor.generate_detailed_advice(plan)
                                st.info(advice)

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
                
                # Filter Bar
                f_col1, f_col2 = st.columns([1, 1])
                with f_col1:
                    assignees = set()
                    for epic in plan.get('epics', []):
                        for story in epic.get('stories', []):
                            for task in story.get('tasks', []):
                                assignees.add(task.get('assignee_name', 'Unassigned'))
                    selected_assignee = st.selectbox("👤 Filter by Assignee", ["All"] + sorted(list(assignees)), key="assignee_filter")
                
                # Render Epics
                for epic in plan.get('epics', []):
                    st.markdown(f"#### 📦 {epic['title']}")
                    
                    for story in epic.get('stories', []):
                        with st.expander(f"📖 {story['title']}", expanded=True):
                            
                            for task in story.get('tasks', []):
                                if selected_assignee != "All" and task.get('assignee_name') != selected_assignee:
                                    continue
                                
                                # Task Row Layout
                                t_status, t_info, t_meta, t_chat = st.columns([2, 4, 1, 3])
                                
                                with t_status:
                                    status_options = ["not_started", "in_progress", "code_review", "unit_testing", "completed", "blocked", "verified_closed"]
                                    current = task.get('status', 'not_started')
                                    # Visual map
                                    s_map = {"not_started": "⚪ Todo", "in_progress": "🔵 IP", "code_review": "🟡 Review", 
                                             "unit_testing": "🟠 Test", "completed": "✅ Done", "blocked": "🔴 Blocked", "verified_closed": "🔒 Closed"}
                                    
                                    new_s = st.selectbox(
                                        "Status", status_options,
                                        index=status_options.index(current) if current in status_options else 0,
                                        key=f"s_{task['task_id']}",
                                        format_func=lambda x: s_map.get(x, x),
                                        label_visibility="collapsed"
                                    )
                                    if new_s != current:
                                        db.update_task_stats(plan['plan_id'], task['task_id'], {"status": new_s})
                                        st.rerun()

                                with t_info:
                                    st.markdown(f"**{task['title']}**")
                                    if task.get('dependencies'):
                                        st.caption(f"🔗 Dep: {', '.join(task['dependencies'])}")
                                    
                                    # --- KNOWLEDGE BASE INTEGRATION ---
                                    # Check for linked KB entries
                                    if 'kb_ingestor' in st.session_state:
                                        kb_entries = st.session_state.kb_ingestor.search_entries(tags=[f"task:{task['task_id']}"])
                                        if kb_entries:
                                            st.markdown(f"📚 **{len(kb_entries)} Knowledge Assets**")
                                            for kbe in kb_entries:
                                                 st.caption(f"📄 [{kbe['category']}] {kbe['content'][:30]}...")

                                with t_meta:
                                    st.caption(f"👤 {task.get('assignee_name')}")
                                    st.caption(f"📅 {task.get('duration_days')}d")
                                
                                with t_chat:
                                    # Comments & Knowledge Actions
                                    comments = task.get('comments', [])
                                    
                                    # Tabs for Task Actions
                                    act_tab1, act_tab2 = st.tabs([f"💬 ({len(comments)})", "📚 Add KB"])
                                    
                                    with act_tab1:
                                        # Chat Interface
                                        with st.container(height=150):
                                            if not comments:
                                                st.caption("Start discussion...")
                                            for c in comments:
                                                bg = "#e3f2fd" if "PM" in c.get('user', '') else "#f5f5f5"
                                                st.markdown(f"""
                                                <div style="background:{bg}; padding:5px; border-radius:5px; margin-bottom:5px; font-size:0.85em;">
                                                    <b>{c.get('user')}</b>: {c.get('text')}
                                                </div>
                                                """, unsafe_allow_html=True)
                                        
                                        new_c = st.text_input("Reply", key=f"nc_{task['task_id']}", label_visibility="collapsed")
                                        if new_c:
                                            from datetime import datetime
                                            user_role = "PM" if pm_mode else "Eng"
                                            new_entry = {
                                                "user": user_role,
                                                "text": new_c,
                                                "timestamp": datetime.now().strftime("%H:%M")
                                            }
                                            updated_comments = comments + [new_entry]
                                            db.update_task_stats(plan['plan_id'], task['task_id'], {"comments": updated_comments})
                                            st.rerun()

                                    with act_tab2:
                                        # Add to Knowledge Base
                                        st.caption("Link code/docs to this task.")
                                        kb_content = st.text_area("Content/Link", key=f"kb_c_{task['task_id']}", height=60)
                                        if st.button("Save to KB", key=f"save_kb_{task['task_id']}"):
                                            if 'kb_ingestor' in st.session_state and kb_content:
                                                st.session_state.kb_ingestor.add_entry(
                                                    content=kb_content, 
                                                    category="task_asset", 
                                                    tags=[f"project:{plan['plan_id']}", f"task:{task['task_id']}"],
                                                    metadata={"author": "PM" if pm_mode else "Eng"}
                                                )
                                                st.success("Saved!")
                                                st.rerun()
                                            else:
                                                st.error("Text required")

                                st.divider()

            # =========================================================
            # VIEW B: TIMELINE (GANTT)
            # =========================================================
            elif board_view == "📅 Timeline (Gantt)":
                st.subheader("Project Timeline")
                
                # Prepare data for Altair
                gantt_data = []
                for epic in plan.get('epics', []):
                    for story in epic.get('stories', []):
                        for task in story.get('tasks', []):
                            gantt_data.append({
                                "Task": task['title'][:30],
                                "Story": story['title'],
                                "Start": task.get('start_day_offset', 1),
                                "End": task.get('start_day_offset', 1) + task.get('duration_days', 1),
                                "Status": task.get('status', 'not_started'),
                                "Assignee": task.get('assignee_name', 'Unassigned'),
                                "TaskId": task['task_id']
                            })
                
                if gantt_data:
                    df_gantt = pd.DataFrame(gantt_data)
                    
                    # Chart
                    chart = alt.Chart(df_gantt).mark_bar().encode(
                        x=alt.X('Start', title='Day Offset'),
                        x2='End',
                        y=alt.Y('Task', sort=alt.EncodingSortField(field="Start", order="ascending")),
                        color=alt.Color('Status', scale=alt.Scale(scheme='tableau10')),
                        tooltip=['Task', 'Start', 'End', 'Assignee', 'Status']
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Interactive Editor to adjust Timeline
                    st.markdown("#### 🔧 Adjust Schedule")
                    st.info("Edit 'Start' (Offset Day) or 'Duration' below to update the plan.")
                    
                    edited_df = st.data_editor(
                        df_gantt[["Task", "Start", "End", "Status", "TaskId"]],
                        key="gantt_editor",
                        disabled=["Task", "Status", "TaskId"],
                        num_rows="fixed"
                    )
                    
                    # Check for changes
                    if st.button("💾 Save Timeline Changes"):
                        changes_made = False
                        # We compare row by row. (Simplified)
                        # In a real app we'd map changes differently, but here we can just iterate.
                        edited_records = edited_df.to_dict('records')
                        
                        # Apply updates locally then save
                        for row in edited_records:
                            tid = row['TaskId']
                            # Find old row
                            old_row = next((x for x in gantt_data if x['TaskId'] == tid), None)
                            if old_row:
                                if old_row['Start'] != row['Start'] or old_row['End'] != row['End']:
                                    # Update specific task
                                    new_dur = max(0.5, row['End'] - row['Start'])
                                    db.update_task_stats(plan['plan_id'], tid, 
                                        {"start_day_offset": row['Start'], "duration_days": new_dur},
                                        user="PM" if pm_mode else "Eng"
                                    )
                                    changes_made = True
                        
                        if changes_made:
                            st.success("Timeline updated!")
                            st.rerun()

            # =========================================================
            # VIEW C: STICKY BOARD
            # =========================================================
            elif board_view == "📌 Sticky Board":
                st.subheader("Brainstorming & Risks")
                st.caption("Add notes, blockers, or ideas here.")
                
                # Get notes
                notes = plan.get("sticky_notes", [])
                
                # Add Note Input
                with st.form("new_note"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        txt = st.text_input("New Stickie Content")
                    with c2:
                        color = st.selectbox("Color", ["yellow", "pink", "green", "blue"], index=0)
                    if st.form_submit_button("➕ Add Stickie"):
                        import uuid
                        new_note = {
                            "id": str(uuid.uuid4()),
                            "text": txt,
                            "color": color,
                            "author": "PM" if pm_mode else "Eng"
                        }
                        notes.append(new_note)
                        db.update_sticky_notes(plan['plan_id'], notes)
                        st.rerun()
                
                # Display Grid
                if not notes:
                    st.info("Board is empty.")
                else:
                    cols = st.columns(3)
                    
                    # CSS for stickies
                    st.markdown("""
                    <style>
                    .stickie {
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 10px;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                        color: #333;
                    }
                    .stickie-yellow { background-color: #fff9c4; border-left: 5px solid #fbc02d; }
                    .stickie-pink { background-color: #f8bbd0; border-left: 5px solid #c2185b; }
                    .stickie-green { background-color: #dcedc8; border-left: 5px solid #689f38; }
                    .stickie-blue { background-color: #bbdefb; border-left: 5px solid #1976d2; }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    for i, note in enumerate(notes):
                        col = cols[i % 3]
                        with col:
                            # Render Stickie
                            c = note.get('color', 'yellow')
                            st.markdown(f"""
                            <div class="stickie stickie-{c}">
                                {note.get('text')}
                                <br><small style='opacity:0.6'>- {note.get('author')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("🗑️", key=f"del_note_{note['id']}"):
                                notes.pop(i)
                                db.update_sticky_notes(plan['plan_id'], notes)
                                st.rerun()

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
