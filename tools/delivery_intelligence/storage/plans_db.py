"""
Plans Database - Simple JSON-based storage for execution plans
"""

import json
import os
from pathlib import Path
from typing import List, Optional
import time
from contextlib import contextmanager

# Cross-platform file locking
try:
    import fcntl  # Unix/Linux/Mac
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    try:
        import msvcrt  # Windows
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False


class PlansDB:
    """Simple JSON file-based storage for execution plans with file locking"""
    
    def __init__(self, db_path: str = "delivery_intelligence/storage/plans.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty database if it doesn't exist
        if not self.db_path.exists():
            self._write_db([])
    
    @contextmanager
    def _lock_file(self, file_handle, timeout=10):
        """
        Cross-platform file locking context manager.
        Prevents concurrent writes from corrupting data.
        """
        if HAS_FCNTL:
            # Unix/Linux/Mac
            start_time = time.time()
            while True:
                try:
                    fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except IOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Could not acquire file lock within timeout")
                    time.sleep(0.1)
            try:
                yield
            finally:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        
        elif HAS_MSVCRT:
            # Windows
            # Save current position to ensure we unlock the same region
            current_pos = file_handle.tell()
            start_time = time.time()
            while True:
                try:
                    file_handle.seek(current_pos)
                    msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except IOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Could not acquire file lock within timeout")
                    time.sleep(0.1)
            try:
                yield
            finally:
                # Must seek back to the locked position to unlock correctly
                file_handle.seek(current_pos)
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            # No locking available - just yield (fallback for unsupported platforms)
            print("WARNING: File locking not available on this platform. Concurrent writes may cause data corruption.")
            yield
    
    def _read_db(self) -> List[dict]:
        """Read all plans from database with file locking"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                with self._lock_file(f):
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_db(self, plans: List[dict]):
        """Write all plans to database with file locking"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            with self._lock_file(f):
                json.dump(plans, f, indent=2, ensure_ascii=False)
    
    
    def _add_audit_entry(self, plan: dict, action: str, user: str = "system", details: dict = None):
        """
        Add an audit trail entry to a plan.
        
        Args:
            plan: The plan to add audit entry to
            action: Action performed (created, updated, status_changed, task_updated, deleted)
            user: User who performed the action
            details: Additional details about the change
        """
        from datetime import datetime
        
        if "history" not in plan:
            plan["history"] = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "details": details or {}
        }
        
        plan["history"].append(entry)
        
        # Keep only last 100 entries to prevent unbounded growth
        if len(plan["history"]) > 100:
            plan["history"] = plan["history"][-100:]
    
    def save_plan(self, plan: dict, user: str = "system") -> str:
        """
        Save a new plan or update existing one with audit trail.
        
        Args:
            plan: Plan to save
            user: User performing the save operation
        """
        plans = self._read_db()
        
        # Check if plan already exists
        existing_index = None
        existing_plan = None
        for i, p in enumerate(plans):
            if p.get("plan_id") == plan.get("plan_id"):
                existing_index = i
                existing_plan = p
                break
        
        if existing_index is not None:
            # Update existing plan - log what changed
            changes = {}
            if existing_plan.get("status") != plan.get("status"):
                changes["status"] = {"old": existing_plan.get("status"), "new": plan.get("status")}
            
            self._add_audit_entry(plan, "updated", user, changes)
            plans[existing_index] = plan
        else:
            # Add new plan
            self._add_audit_entry(plan, "created", user)
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
    
    def delete_plan(self, plan_id: str, user: str = "system") -> bool:
        """
        Delete a plan by ID with audit trail.
        
        Args:
            plan_id: ID of plan to delete
            user: User performing the deletion
        """
        plans = self._read_db()
        
        # Find and log deletion
        for plan in plans:
            if plan.get("plan_id") == plan_id:
                self._add_audit_entry(plan, "deleted", user)
                break
        
        filtered_plans = [p for p in plans if p.get("plan_id") != plan_id]
        
        if len(filtered_plans) < len(plans):
            self._write_db(filtered_plans)
            return True
        return False
    
    def update_plan_status(self, plan_id: str, new_status: str, user: str = "system") -> bool:
        """
        Update plan status with audit trail.
        
        Args:
            plan_id: ID of plan to update
            new_status: New status value
            user: User performing the update
        """
        plan = self.get_plan(plan_id)
        if plan:
            old_status = plan.get("status")
            plan["status"] = new_status
            
            self._add_audit_entry(plan, "status_changed", user, {
                "old_status": old_status,
                "new_status": new_status
            })
            
            self.save_plan(plan, user)
            return True
        return False

    def update_task_stats(self, plan_id: str, task_id: str, updates: dict, user: str = "system") -> bool:
        """
        Update specific fields of a task with audit trail.
        
        Args:
            plan_id: ID of the plan
            task_id: ID of the task to update
            updates: Dictionary of fields to update
            user: User performing the update
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return False
            
        found = False
        task_title = None
        old_values = {}
        
        for epic in plan.get("epics", []):
            for story in epic.get("stories", []):
                for task in story.get("tasks", []):
                    if task.get("task_id") == task_id:
                        task_title = task.get("title")
                        
                        # Track old values for audit
                        for key in updates.keys():
                            if key in task:
                                old_values[key] = task[key]
                        
                        # Update fields
                        for key, value in updates.items():
                             task[key] = value
                        found = True
                        break
                if found: break
            if found: break
            
            
        if found:
            # Add audit entry
            self._add_audit_entry(plan, "task_updated", user, {
                "task_id": task_id,
                "task_title": task_title,
                "updates": updates,
                "old_values": old_values
            })
            
            self.save_plan(plan, user)
            return True
        return False

    def update_sticky_notes(self, plan_id: str, notes: list, user: str = "system") -> bool:
        """
        Update the entire list of sticky notes for a plan.
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return False
            
        plan["sticky_notes"] = notes
        # We generally don't audit every sticky move/edit to avoid spam, or we can:
        # self._add_audit_entry(plan, "notes_updated", user)
        self.save_plan(plan, user)
        return True
