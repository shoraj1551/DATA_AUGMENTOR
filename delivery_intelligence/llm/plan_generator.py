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

Your task is to break down project requirements into a structured execution plan.

CRITICAL RULES:
- Return ONLY valid JSON
- NO explanations, NO markdown, NO comments
- Generate realistic, actionable work items
- Include clear acceptance criteria for stories
- Break down complex work into manageable tasks

Output format:
{
  "title": "Project Title",
  "description": "Brief project description",
  "epics": [
    {
      "title": "Epic Title",
      "description": "Epic description",
      "stories": [
        {
          "title": "Story Title",
          "description": "Story description",
          "acceptance_criteria": ["Criterion 1", "Criterion 2"],
          "tasks": [
            {
              "title": "Task Title",
              "description": "Task description"
            }
          ]
        }
      ]
    }
  ]
}"""

    user_prompt = f"""Project Requirements:
{prompt}

Engineer Experience Level: {engineer_level}

Generate a complete execution plan with:
1. 2-4 epics (major work streams)
2. 3-6 stories per epic (user-facing features)
3. 3-8 tasks per story (technical implementation steps)

Make the plan realistic and actionable for a {engineer_level}-level engineer."""

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
        "epics": []
    }
    
    # Add IDs to epics, stories, and tasks
    for epic_data in plan_data.get("epics", []):
        epic = {
            "epic_id": str(uuid.uuid4()),
            "title": epic_data.get("title", "Untitled Epic"),
            "description": epic_data.get("description", ""),
            "stories": []
        }
        
        for story_data in epic_data.get("stories", []):
            story = {
                "story_id": str(uuid.uuid4()),
                "title": story_data.get("title", "Untitled Story"),
                "description": story_data.get("description", ""),
                "acceptance_criteria": story_data.get("acceptance_criteria", []),
                "tasks": []
            }
            
            for task_data in story_data.get("tasks", []):
                task = {
                    "task_id": str(uuid.uuid4()),
                    "title": task_data.get("title", "Untitled Task"),
                    "description": task_data.get("description", ""),
                    "status": "todo"
                }
                story["tasks"].append(task)
            
            epic["stories"].append(story)
        
        plan["epics"].append(epic)
    
    return plan
