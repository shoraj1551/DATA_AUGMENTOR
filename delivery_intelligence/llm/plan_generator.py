"""
Plan Generator - LLM-based execution plan generation
"""

from llm.client import get_client
from config.settings import get_model_for_feature
import json
import uuid
from datetime import datetime


def generate_execution_plan(prompt: str, engineer_level: str = "mid", team_members=None) -> dict:
    """
    Generate a structured execution plan using LLM, optionally with team assignments.
    
    Args:
        prompt (str): Project description
        engineer_level (str): Default experience level (fallback)
        team_members (list[dict]): Optional list of team members 
                                   [{"id": "1", "name": "Alice", "role": "Senior Backend", "level": "senior"}]
    
    Returns:
        dict: Structured plan with epics, stories, and tasks
    """
    
    # Construct Team Context
    team_context = ""
    if team_members and len(team_members) > 0:
        team_context = "TEAM ROSTER (Assign tasks to these people based on fit):\n"
        for member in team_members:
            team_context += f"- {member['name']} (ID: {member['id']}): {member['role']} [{member['level'].upper()}]\n"
        
        assign_instruction = "CRITICAL: Assign every task to a specific 'assignee_id' from the roster. Choose the best fit for the task complexity."
    else:
        team_context = f"NO TEAM DEFINED. Assume a single {engineer_level.upper()} engineer."
        assign_instruction = "Assign tasks to 'unassigned'."

    system_prompt = f"""You are an expert Technical Project Manager and Architect.

Your task is to break down project requirements into a detailed PROJECT PLAN with TEAM ASSIGNMENTS.

{assign_instruction}

CRITICAL RULES:
1.  **Sequencing**: Order tasks logically. Identify dependencies.
2.  **Granularity**: tasks should be 2-8 hours max.
3.  **Estimates**: accurate hours based on the assignee's level (Seniors are faster, Juniors need buffer).
4.  **JSON ONLY**: Return strictly valid JSON.

Output format:
{{
  "title": "Project Title",
  "description": "Executive summary",
  "estimated_total_days": 10,
  "epics": [
    {{
      "title": "Epic Title",
      "description": "High level scope",
      "estimated_days": 5,
      "stories": [
        {{
          "title": "Story Title",
          "description": "User facing feature",
          "estimated_hours": 16,
          "acceptance_criteria": ["Criteria 1", "Criteria 2"],
          "tasks": [
            {{
              "title": "Task Title",
              "description": "Technical step",
              "estimated_hours": 4,
              "assignee_id": "member_id_or_null",
              "assignee_name": "Name or Unassigned",
              "status": "not_started",
              "start_day_offset": 1,  # Day number this task starts (1-indexed)
              "duration_days": 0.5
            }}
          ]
        }}
      ]
    }}
  ]
}}"""

    # Define multipliers for experience levels (for fallback or general guidance)
    level_guidance = {
        "junior": "Junior: slower execution (1.5x), needs detailed specs.",
        "mid": "Mid-level: standard execution (1.0x).",
        "senior": "Senior: fast execution (0.7x), handles ambiguity.",
        "lead": "Lead: very fast (0.5x) but limited availability due to valid management overhead."
    }
    
    guidance = level_guidance.get(engineer_level, level_guidance["mid"])

    user_prompt = f"""Project Requirements:
{prompt}

{team_context}

Guidance: {guidance}

Generate the execution plan. 
- Ensure tasks are evenly distributed if multiple members have similar skills.
- Senior/Lead should handle Architecture & difficult Core logic.
- Juniors/Mids should handle implementation, testing, and UI.
- Sequence tasks so blockers are minimized (e.g., DB design before API impl).
"""

    response = get_client().chat.completions.create(
        model=get_model_for_feature("delivery_intelligence"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # Parse LLM response
    plan_data = json.loads(response.choices[0].message.content)
    
    # Add metadata and IDs
    plan = {
        "plan_id": str(uuid.uuid4()),
        "title": plan_data.get("title", "Untitled Plan"),
        "description": plan_data.get("description", ""),
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "engineer_level": engineer_level if not team_members else "Team",
        "team": team_members if team_members else [],
        "estimated_total_days": plan_data.get("estimated_total_days", 0),
        "epics": []
    }
    
    # Add IDs to epics, stories, and tasks
    for epic_data in plan_data.get("epics", []):
        epic = {
            "epic_id": str(uuid.uuid4()),
            "title": epic_data.get("title", "Untitled Epic"),
            "description": epic_data.get("description", ""),
            "estimated_days": epic_data.get("estimated_days", 0),
            "stories": []
        }
        
        for story_data in epic_data.get("stories", []):
            story = {
                "story_id": str(uuid.uuid4()),
                "title": story_data.get("title", "Untitled Story"),
                "description": story_data.get("description", ""),
                "estimated_hours": story_data.get("estimated_hours", 0),
                "acceptance_criteria": story_data.get("acceptance_criteria", []),
                "tasks": []
            }
            
            for task_data in story_data.get("tasks", []):
                # Ensure status is strictly one of the allowed set
                status = "not_started"
                current_status = task_data.get("status", "not_started").lower().replace(" ", "_")
                if current_status in ["done", "completed"]:
                    status = "completed"
                elif current_status in ["in_progress", "active"]:
                    status = "in_progress"
                
                task = {
                    "task_id": str(uuid.uuid4()),
                    "title": task_data.get("title", "Untitled Task"),
                    "description": task_data.get("description", ""),
                    "estimated_hours": task_data.get("estimated_hours", 0),
                    "status": status,
                    "assignee_id": task_data.get("assignee_id"),
                    "assignee_name": task_data.get("assignee_name", "Unassigned"),
                    "start_day_offset": task_data.get("start_day_offset", 1),
                    "comments": []
                }
                story["tasks"].append(task)
            
            epic["stories"].append(story)
        
        plan["epics"].append(epic)
    
    return plan
