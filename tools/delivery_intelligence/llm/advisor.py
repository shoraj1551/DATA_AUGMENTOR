
"""
AI Advisor for Delivery Intelligence
Analyzes execution plans to identify risks, blockers, and provide suggestions.
"""
from typing import Dict, List, Any
import json
from config.settings import get_model_for_feature
from common.llm.client import get_client
from tools.delivery_intelligence.storage.plans_db import PlansDB

class PlanAdvisor:
    def __init__(self):
        self.client = get_client()
        self.db = PlansDB()

    def analyze_plan_health(self, plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Analyze a plan and return a list of alerts/insights.
        
        Returns:
            List of dicts: [{ "type": "warning|danger|info|success", "message": "...", "task_id": "optional" }]
        """
        alerts = []
        
        # 1. Static Analysis (Fast)
        alerts.extend(self._check_stalled_tasks(plan))
        alerts.extend(self._check_blockers_in_comments(plan))
        
        # 2. LLM Analysis (Deep)
        # We only run this if there are comments or complex states to save tokens
        # For now, let's keep it lightweight and focused on comment sentiment analysis
        
        return alerts

    def _check_stalled_tasks(self, plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check for tasks stuck in 'in_progress' for too long (mock logic for now)"""
        alerts = []
        # In a real app, we'd compare timestamp of last update vs now.
        # Here we just look for 'blocked' status
        
        for epic in plan.get('epics', []):
            for story in epic.get('stories', []):
                for task in story.get('tasks', []):
                    if task.get('status') == 'blocked':
                        alerts.append({
                            "type": "danger",
                            "message": f"⛔ Task '{task['title']}' is marked as BLOCKED.",
                            "task_id": task['task_id']
                        })
        return alerts

    def _check_blockers_in_comments(self, plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Scan comments for keywords indicating hidden blockers"""
        alerts = []
        keywords = ["blocked", "stuck", "waiting for", "dependency", "fail", "error"]
        
        for epic in plan.get('epics', []):
            for story in epic.get('stories', []):
                for task in story.get('tasks', []):
                    # Skip if already marked blocked
                    if task.get('status') == 'blocked':
                        continue
                        
                    comments = task.get('comments', [])
                    if not comments:
                        continue
                        
                    # Check last few comments
                    recent_text = " ".join([c.get('text', '').lower() for c in comments[-3:]])
                    
                    for kw in keywords:
                        if kw in recent_text:
                            alerts.append({
                                "type": "warning",
                                "message": f"⚠️ Task '{task['title']}' might be at risk. Comment mentions '{kw}'.",
                                "task_id": task['task_id']
                            })
                            break
        return alerts

    def generate_detailed_advice(self, plan: Dict[str, Any]) -> str:
        """
        Generate a comprehensive textual advice summary using LLM.
        """
        try:
            # Simplify context for LLM
            context = {
                "title": plan['title'],
                "status": plan['status'],
                "progress": "In Progress", # Calculate real progress
                "open_issues": []
            }
            
            # Extract relevant issues
            for epic in plan.get('epics', []):
                for story in epic.get('stories', []):
                    for task in story.get('tasks', []):
                        if task['status'] in ['blocked', 'in_progress']:
                             context['open_issues'].append({
                                 "task": task['title'],
                                 "status": task['status'],
                                 "comments": [c['text'] for c in task.get('comments', [])[-1:]]
                             })
            
            prompt = f"""
            Analyze this project status and provide 3 bullet points of proactive advice for the Project Manager.
            Focus on risks and bottlenecks.
            
            Project Context:
            {json.dumps(context, indent=2)}
            """
            
            response = self.client.chat.completions.create(
                model=get_model_for_feature("delivery_intelligence"),
                messages=[
                    {"role": "system", "content": "You are an expert Agile Project Manager advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return "Could not generate advice at this time."
