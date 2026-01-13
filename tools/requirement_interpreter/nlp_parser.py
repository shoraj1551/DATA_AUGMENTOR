"""
NLP Parser - Extract key entities from business text
"""
import re
from typing import Dict, List, Any


class NLPParser:
    """Parse business requirements from natural language"""
    
    def __init__(self):
        """Initialize NLP parser"""
        self.metric_keywords = ['revenue', 'sales', 'profit', 'cost', 'count', 'average', 'total', 'rate', 'percentage']
        self.time_keywords = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'last', 'this', 'next']
        self.filter_keywords = ['where', 'for', 'by', 'in', 'from', 'with', 'excluding', 'including']
    
    def parse_requirement(self, text: str) -> Dict[str, Any]:
        """
        Parse business requirement text
        
        Args:
            text: Business requirement text
            
        Returns:
            Parsed entities and intent
        """
        text_lower = text.lower()
        
        return {
            'original_text': text,
            'metrics': self._extract_metrics(text_lower),
            'time_dimensions': self._extract_time_dimensions(text_lower),
            'filters': self._extract_filters(text_lower),
            'entities': self._extract_entities(text_lower),
            'intent': self._classify_intent(text_lower)
        }
    
    def _extract_metrics(self, text: str) -> List[str]:
        """Extract metric mentions"""
        metrics = []
        for keyword in self.metric_keywords:
            if keyword in text:
                # Extract context around keyword
                pattern = rf'\b\w*{keyword}\w*\b'
                matches = re.findall(pattern, text)
                metrics.extend(matches)
        return list(set(metrics))
    
    def _extract_time_dimensions(self, text: str) -> List[str]:
        """Extract time-related dimensions"""
        time_dims = []
        for keyword in self.time_keywords:
            if keyword in text:
                time_dims.append(keyword)
        
        # Extract specific dates/periods
        date_patterns = [
            r'\b\d{4}\b',  # Year
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\b',  # Month
            r'\bq[1-4]\b',  # Quarter
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            time_dims.extend(matches)
        
        return list(set(time_dims))
    
    def _extract_filters(self, text: str) -> List[str]:
        """Extract filter conditions"""
        filters = []
        
        # Look for filter keywords and extract context
        for keyword in self.filter_keywords:
            if keyword in text:
                # Extract phrase after keyword
                pattern = rf'{keyword}\s+(\w+(?:\s+\w+){{0,3}})'
                matches = re.findall(pattern, text)
                filters.extend(matches)
        
        return filters
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract business entities (products, regions, etc.)"""
        entities = []
        
        # Common entity patterns
        entity_patterns = [
            r'\b(product|customer|region|country|city|department|team|category)\w*\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'  # Capitalized phrases
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _classify_intent(self, text: str) -> str:
        """Classify the intent of the requirement"""
        if any(word in text for word in ['compare', 'vs', 'versus', 'difference']):
            return 'comparison'
        elif any(word in text for word in ['trend', 'over time', 'growth', 'change']):
            return 'trend_analysis'
        elif any(word in text for word in ['breakdown', 'by', 'split', 'segment']):
            return 'breakdown'
        elif any(word in text for word in ['top', 'bottom', 'best', 'worst', 'highest', 'lowest']):
            return 'ranking'
        elif any(word in text for word in ['total', 'sum', 'aggregate', 'overall']):
            return 'aggregation'
        else:
            return 'general_query'
