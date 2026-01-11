"""
Plan Generator - LLM-based execution plan generation
"""

from llm.client import get_client
from config.settings import MODEL_NAME
import json
import uuid
from datetime import datetime


def generate_execution_plan(prompt: str, engineer_level: str = "mid") -> dict:
    """
    Generate an execution plan with epics, stories, and tasks from a user prompt.
    
    Args:
        prompt: User description of the project/feature
        engineer_level: Experience level (junior, mid, senior, lead)
    
    Returns:
        dict: Structured plan with epics, stories, and tasks
    """
    
    system_prompt = """You are an expert technical project planner for data and platform teams.

Your task is to break down project requirements into a structured execution plan with REALISTIC TIMELINE ESTIMATES.

CRITICAL RULES:
- Return ONLY valid JSON
- NO explanations, NO markdown, NO comments
- Generate realistic, actionable work items
- ESTIMATE TIME for every single item based on the engineer's experience level
- Include clear acceptance criteria for stories or "tasks" if stories are not used
- Break down complex work into manageable tasks

Output format:
{
  "title": "Project Title",
  "description": "Brief project description",
  "estimated_total_days": 10,
  "epics": [
    {
      "title": "Epic Title",
      "description": "Epic description",
      "estimated_days": 5,
      "stories": [
        {
          "title": "Story Title",
          "description": "Story description",
          "estimated_hours": 16,
          "acceptance_criteria": ["Criterion 1", "Criterion 2"],
          "tasks": [
            {
              "title": "Task Title",
              "description": "Task description",
              "estimated_hours": 4
            }
          ]
        }
      ]
    }
  ]
}"""

    # Define multipliers for experience levels (Junior takes longer)
    level_guidance = {
        "junior": "Assume a JUNIOR engineer: Needs detailed tasks, explicit instructions. Multiply standard estimates by 1.5x - 2.0x.",
        "mid": "Assume a MID-LEVEL engineer: Needs clear requirements but less hand-holding. Standard industry estimates.",
        "senior": "Assume a SENIOR engineer: Can handle ambiguity. Multiply standard estimates by 0.7x - 0.8x.",
        "lead": "Assume a LEAD engineer: strategic focus, very fast execution. Multiply standard estimates by 0.5x - 0.7x but add time for architecture/mentoring."
    }
    
    guidance = level_guidance.get(engineer_level, level_guidance["mid"])

    user_prompt = f"""Project Requirements:
{prompt}

Engineer Experience Level: {engineer_level.upper()}
{guidance}

Generate a complete execution plan with:
1. 2-4 epics (major work streams)
2. 3-6 stories per epic
3. 3-8 tasks per story
4. REALISTIC TIME ESTIMATES (Days for Epics, Hours for Stories/Tasks)

IMPORTANT: The sum of task hours should roughly equal story hours. Sum of story hours should roughly equal epic days (assume 6 productive hours/day)."""

    response = get_client().chat.completions.create(
        model=MODEL_NAME,
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
        "engineer_level": engineer_level,
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
                task = {
                    "task_id": str(uuid.uuid4()),
                    "title": task_data.get("title", "Untitled Task"),
                    "description": task_data.get("description", ""),
                    "estimated_hours": task_data.get("estimated_hours", 0),
                    "status": "todo"
                }
                story["tasks"].append(task)
            
            epic["stories"].append(story)
        
        plan["epics"].append(epic)
    
    return plan
