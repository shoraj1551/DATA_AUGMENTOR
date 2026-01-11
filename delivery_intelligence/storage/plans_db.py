"""
Plans Database - Simple JSON-based storage for execution plans
"""

import json
import os
from pathlib import Path
from typing import List, Optional


class PlansDB:
    """Simple JSON file-based storage for execution plans"""
    
    def __init__(self, db_path: str = "delivery_intelligence/storage/plans.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty database if it doesn't exist
        if not self.db_path.exists():
            self._write_db([])
    
    def _read_db(self) -> List[dict]:
        """Read all plans from database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_db(self, plans: List[dict]):
        """Write all plans to database"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(plans, f, indent=2, ensure_ascii=False)
    
    def save_plan(self, plan: dict) -> str:
        """Save a new plan or update existing one"""
        plans = self._read_db()
        
        # Check if plan already exists
        existing_index = None
        for i, p in enumerate(plans):
            if p.get("plan_id") == plan.get("plan_id"):
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing plan
            plans[existing_index] = plan
        else:
            # Add new plan
            plans.append(plan)
        
        self._write_db(plans)
        return plan.get("plan_id")
    
    def get_plan(self, plan_id: str) -> Optional[dict]:
        """Get a plan by ID"""
        plans = self._read_db()
        for plan in plans:
            if plan.get("plan_id") == plan_id:
                return plan
        return None
    
    def get_all_plans(self) -> List[dict]:
        """Get all plans"""
        return self._read_db()
    
    def get_plans_by_status(self, status: str) -> List[dict]:
        """Get plans filtered by status"""
        plans = self._read_db()
        return [p for p in plans if p.get("status") == status]
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan by ID"""
        plans = self._read_db()
        filtered_plans = [p for p in plans if p.get("plan_id") != plan_id]
        
        if len(filtered_plans) < len(plans):
            self._write_db(filtered_plans)
            return True
        return False
    
    def update_plan_status(self, plan_id: str, new_status: str) -> bool:
        """Update plan status"""
        plan = self.get_plan(plan_id)
        if plan:
            plan["status"] = new_status
            self.save_plan(plan)
            return True
        return False

    def update_task_stats(self, plan_id: str, task_id: str, updates: dict) -> bool:
        """
        Update specific fields of a task (status, actuals, comments)
        
        Args:
            plan_id: ID of the plan
            task_id: ID of the task to update
            updates: Dictionary of fields to update (e.g. {"status": "in_progress", "actual_hours": 4})
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return False
            
        found = False
        for epic in plan.get("epics", []):
            for story in epic.get("stories", []):
                for task in story.get("tasks", []):
                    if task.get("task_id") == task_id:
                        # Update fields
                        for key, value in updates.items():
                             task[key] = value
                        found = True
                        break
                if found: break
            if found: break
            
        if found:
            self.save_plan(plan)
            return True
        return False
