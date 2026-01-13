"""
Content Ingestor - Capture project knowledge
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class ContentIngestor:
    """Ingest and store project knowledge"""
    
    def __init__(self, kb_path: str = None):
        """Initialize content ingestor"""
        if kb_path is None:
            kb_path = str(Path.home() / ".dataaugmentor" / "knowledge_base.json")
        
        self.kb_path = Path(kb_path)
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.kb_path.exists():
            self._save_kb([])
    
    def _load_kb(self) -> List[Dict]:
        """Load knowledge base"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_kb(self, kb: List[Dict]):
        """Save knowledge base"""
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2)
    
    def add_entry(self, content: str, category: str, tags: List[str] = None, 
                  metadata: Dict = None) -> Dict:
        """
        Add entry to knowledge base
        
        Args:
            content: Content to store
            category: Category (code, docs, decision, query, etc.)
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Created entry
        """
        kb = self._load_kb()
        
        entry = {
            'id': len(kb) + 1,
            'content': content,
            'category': category,
            'tags': tags or [],
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        kb.append(entry)
        self._save_kb(kb)
        
        return entry
    
    def search_entries(self, query: str = None, category: str = None, 
                      tags: List[str] = None) -> List[Dict]:
        """
        Search knowledge base
        
        Args:
            query: Text to search for
            category: Filter by category
            tags: Filter by tags
            
        Returns:
            Matching entries
        """
        kb = self._load_kb()
        results = kb
        
        # Filter by category
        if category:
            results = [e for e in results if e.get('category') == category]
        
        # Filter by tags
        if tags:
            results = [e for e in results if any(t in e.get('tags', []) for t in tags)]
        
        # Search in content
        if query:
            query_lower = query.lower()
            results = [
                e for e in results 
                if query_lower in e.get('content', '').lower()
            ]
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        kb = self._load_kb()
        return list(set(e.get('category') for e in kb if e.get('category')))
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        kb = self._load_kb()
        all_tags = []
        for entry in kb:
            all_tags.extend(entry.get('tags', []))
        return list(set(all_tags))
    
    def delete_entry(self, entry_id: int):
        """Delete an entry"""
        kb = self._load_kb()
        kb = [e for e in kb if e.get('id') != entry_id]
        self._save_kb(kb)
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        kb = self._load_kb()
        return {
            'total_entries': len(kb),
            'categories': len(self.get_all_categories()),
            'tags': len(self.get_all_tags()),
            'latest_entry': kb[-1].get('created_at') if kb else None
        }
