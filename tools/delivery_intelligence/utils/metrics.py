"""
Metrics Service - Calculate velocity, burndown, and project health metrics
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


def calculate_velocity(plan: dict) -> Dict[str, float]:
    """
    Calculate team velocity metrics.
    
    Returns:
        {
            "completed_hours": float,
            "days_worked": float,
            "velocity_per_day": float,
            "estimated_total_hours": float,
            "remaining_hours": float,
            "predicted_days_remaining": float
        }
    """
    completed_hours = 0.0
    estimated_total_hours = 0.0
    remaining_hours = 0.0
    
    for epic in plan.get("epics", []):
        for story in epic.get("stories", []):
            for task in story.get("tasks", []):
                estimated = task.get("estimated_hours", 0)
                actual = task.get("actual_hours", 0)
                status = task.get("status", "not_started")
                
                estimated_total_hours += estimated
                
                if status in ["completed", "verified_closed"]:
                    completed_hours += actual if actual > 0 else estimated
                else:
                    remaining_hours += estimated
    
    # Calculate days worked from plan creation date
    created_at = plan.get("created_at", datetime.now().isoformat())
    created_date = datetime.fromisoformat(created_at.split("T")[0])
    days_worked = max(1, (datetime.now() - created_date).days)
    
    # Calculate velocity (hours completed per day)
    velocity_per_day = completed_hours / days_worked if days_worked > 0 else 0
    
    # Predict remaining days
    predicted_days_remaining = remaining_hours / velocity_per_day if velocity_per_day > 0 else 0
    
    return {
        "completed_hours": round(completed_hours, 1),
        "days_worked": days_worked,
        "velocity_per_day": round(velocity_per_day, 1),
        "estimated_total_hours": round(estimated_total_hours, 1),
        "remaining_hours": round(remaining_hours, 1),
        "predicted_days_remaining": round(predicted_days_remaining, 1)
    }


def calculate_burndown_data(plan: dict) -> List[Dict]:
    """
    Generate burndown chart data points.
    
    Returns list of:
        {
            "day": int,
            "date": str,
            "ideal_remaining": float,
            "actual_remaining": float
        }
    """
    # Get velocity metrics
    metrics = calculate_velocity(plan)
    total_hours = metrics["estimated_total_hours"]
    days_worked = metrics["days_worked"]
    
    # Calculate ideal burndown (linear)
    estimated_days = plan.get("estimated_total_days", 10)
    ideal_burn_rate = total_hours / estimated_days if estimated_days > 0 else 0
    
    # Generate data points
    burndown_data = []
    
    # Day 0: Start
    burndown_data.append({
        "day": 0,
        "date": plan.get("created_at", "")[:10],
        "ideal_remaining": total_hours,
        "actual_remaining": total_hours
    })
    
    # Current day
    actual_remaining = metrics["remaining_hours"]
    ideal_remaining = max(0, total_hours - (ideal_burn_rate * days_worked))
    
    burndown_data.append({
        "day": days_worked,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "ideal_remaining": round(ideal_remaining, 1),
        "actual_remaining": round(actual_remaining, 1)
    })
    
    # Projected completion
    if metrics["velocity_per_day"] > 0:
        total_days_projected = days_worked + metrics["predicted_days_remaining"]
        burndown_data.append({
            "day": int(total_days_projected),
            "date": (datetime.now() + timedelta(days=metrics["predicted_days_remaining"])).strftime("%Y-%m-%d"),
            "ideal_remaining": 0,
            "actual_remaining": 0
        })
    
    return burndown_data


def calculate_task_health(plan: dict) -> Dict[str, int]:
    """
    Calculate task health metrics (on-track, at-risk, overdue).
    
    Returns:
        {
            "on_track": int,
            "at_risk": int,
            "overdue": int,
            "blocked": int
        }
    """
    on_track = 0
    at_risk = 0
    overdue = 0
    blocked = 0
    
    for epic in plan.get("epics", []):
        for story in epic.get("stories", []):
            for task in story.get("tasks", []):
                status = task.get("status", "not_started")
                estimated_hours = task.get("estimated_hours", 0)
                actual_hours = task.get("actual_hours", 0)
                
                if status == "blocked":
                    blocked += 1
                elif status in ["completed", "verified_closed"]:
                    # Already done, count as on-track
                    on_track += 1
                elif actual_hours > estimated_hours * 1.2:
                    # 20% over estimate = overdue
                    overdue += 1
                elif actual_hours > estimated_hours * 0.8:
                    # 80-100% of estimate = at risk
                    at_risk += 1
                else:
                    on_track += 1
    
    return {
        "on_track": on_track,
        "at_risk": at_risk,
        "overdue": overdue,
        "blocked": blocked
    }


def get_assignee_workload(plan: dict) -> List[Dict]:
    """
    Calculate workload distribution across team members.
    
    Returns list of:
        {
            "assignee": str,
            "total_hours": float,
            "completed_hours": float,
            "remaining_hours": float,
            "task_count": int
        }
    """
    workload = {}
    
    for epic in plan.get("epics", []):
        for story in epic.get("stories", []):
            for task in story.get("tasks", []):
                assignee = task.get("assignee_name", "Unassigned")
                estimated = task.get("estimated_hours", 0)
                actual = task.get("actual_hours", 0)
                status = task.get("status", "not_started")
                
                if assignee not in workload:
                    workload[assignee] = {
                        "assignee": assignee,
                        "total_hours": 0,
                        "completed_hours": 0,
                        "remaining_hours": 0,
                        "task_count": 0
                    }
                
                workload[assignee]["total_hours"] += estimated
                workload[assignee]["task_count"] += 1
                
                if status in ["completed", "verified_closed"]:
                    workload[assignee]["completed_hours"] += actual if actual > 0 else estimated
                else:
                    workload[assignee]["remaining_hours"] += estimated
    
    # Convert to list and sort by total hours
    result = list(workload.values())
    result.sort(key=lambda x: x["total_hours"], reverse=True)
    
    return result
