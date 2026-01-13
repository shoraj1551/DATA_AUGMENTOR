"""
User Preferences Storage
Persistent storage for user settings like favorites
"""
import json
import os
from pathlib import Path
from typing import Set


class UserPreferences:
    """Manage user preferences with persistent storage"""
    
    def __init__(self):
        """Initialize preferences storage"""
        self.prefs_dir = Path.home() / ".dataaugmentor"
        self.prefs_file = self.prefs_dir / "preferences.json"
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory and file exist"""
        try:
            self.prefs_dir.mkdir(parents=True, exist_ok=True)
            if not self.prefs_file.exists():
                self._save_prefs({"favorite_tools": []})
        except Exception as e:
            print(f"Warning: Could not create preferences storage: {e}")
    
    def _load_prefs(self) -> dict:
        """Load preferences from file"""
        try:
            if self.prefs_file.exists():
                with open(self.prefs_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load preferences: {e}")
        return {"favorite_tools": []}
    
    def _save_prefs(self, prefs: dict):
        """Save preferences to file"""
        try:
            with open(self.prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")
    
    def get_favorites(self) -> Set[str]:
        """Get favorite tools"""
        prefs = self._load_prefs()
        return set(prefs.get("favorite_tools", []))
    
    def add_favorite(self, tool_id: str):
        """Add a tool to favorites"""
        prefs = self._load_prefs()
        favorites = set(prefs.get("favorite_tools", []))
        favorites.add(tool_id)
        prefs["favorite_tools"] = list(favorites)
        self._save_prefs(prefs)
    
    def remove_favorite(self, tool_id: str):
        """Remove a tool from favorites"""
        prefs = self._load_prefs()
        favorites = set(prefs.get("favorite_tools", []))
        favorites.discard(tool_id)
        prefs["favorite_tools"] = list(favorites)
        self._save_prefs(prefs)
    
    def toggle_favorite(self, tool_id: str):
        """Toggle a tool's favorite status"""
        favorites = self.get_favorites()
        if tool_id in favorites:
            self.remove_favorite(tool_id)
        else:
            self.add_favorite(tool_id)
