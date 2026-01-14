"""
Insight Generator - LLM-powered insights from profiling data
"""
from common.llm.client import get_client
import json


class InsightGenerator:
    """Generate human-readable insights using LLM"""
    
    def __init__(self):
        """Initialize insight generator"""
        self.client = get_client()
    
    def generate_insights(self, profile: dict, anomalies: list) -> dict:
        """
        Generate insights from profile data
        
        Args:
            profile: Dataset profile dictionary
            anomalies: List of detected anomalies
            
        Returns:
            Dictionary with insights and recommendations
        """
        prompt = self._build_prompt(profile, anomalies)
        
        try:
            from common.llm.client import call_with_fallback
            
            response = call_with_fallback(
                feature_name="data_profiling",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst expert. Analyze dataset profiles and provide clear, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            insights_text = response.choices[0].message.content
            return self._parse_insights(insights_text)
            
        except Exception as e:
            return {
                'summary': 'Error generating insights',
                'error': str(e),
                'key_findings': [],
                'recommendations': []
            }
    
    def _build_prompt(self, profile: dict, anomalies: list) -> str:
        """Build prompt for LLM with actual data context"""
        
        # Build column details
        column_details = []
        for col in profile['columns'][:20]:  # First 20 columns
            col_info = f"- **{col['name']}** ({col.get('dtype', 'unknown')}): "
            col_info += f"{col['unique']} unique values, "
            col_info += f"{col['missing']} missing ({(col['missing']/profile['overview']['rows']*100):.1f}%)"
            
            # Add top values for categorical columns
            if col.get('dtype') == 'object' and col['unique'] < 10:
                col_info += f" | Top values: {col.get('top_value', 'N/A')}"
            
            column_details.append(col_info)
        
        if len(profile['columns']) > 20:
            column_details.append(f"... and {len(profile['columns']) - 20} more columns")
        
        columns_text = "\n".join(column_details)
        
        # Build anomalies text
        anomalies_text = ""
        if anomalies:
            for anomaly in anomalies[:10]:  # Top 10 anomalies
                anomalies_text += f"- {anomaly.get('severity', 'unknown').upper()}: {anomaly.get('type', 'Unknown')} in column '{anomaly.get('column', 'N/A')}' - {anomaly.get('detail', 'No details')}\n"
        else:
            anomalies_text = "No anomalies detected"
        
        return f"""Analyze this SPECIFIC dataset and provide ACCURATE insights based on the ACTUAL data below.

CRITICAL: Base your analysis ONLY on the column names, data types, and statistics provided. Do NOT make up generic insights.

DATASET OVERVIEW:
- Rows: {profile['overview']['rows']:,}
- Columns: {profile['overview']['columns']}
- Memory: {profile['overview']['memory_usage_mb']} MB
- Duplicates: {profile['overview']['duplicate_rows']}
- Total Missing Values: {profile['overview']['total_missing']:,}

ACTUAL COLUMNS IN THIS DATASET:
{columns_text}

ANOMALIES DETECTED:
{anomalies_text}

INSTRUCTIONS:
1. Look at the ACTUAL column names above (e.g., if you see 'CO(GT)', 'PT08.S1(CO)', mention those specifically)
2. Reference REAL data types and statistics shown
3. Do NOT mention generic columns like "email", "customer", "segment" unless they actually exist
4. Be specific about which columns have issues

Format your response as:

SUMMARY:
[2-3 sentence overview mentioning ACTUAL column names from the data]

KEY FINDINGS:
- [Finding 1 with specific column names]
- [Finding 2]
- [Finding 3]

DATA QUALITY ISSUES:
- [Issue 1 with specific column name]
- [Issue 2]

RECOMMENDATIONS:
- [Action 1 for specific column]
- [Action 2]
- [Action 3]
"""
    
    def _parse_insights(self, text: str) -> dict:
        """Parse LLM response into structured format"""
        sections = {
            'summary': '',
            'key_findings': [],
            'quality_issues': [],
            'recommendations': []
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            line_upper = line.upper()
            
            if 'SUMMARY' in line_upper and (line_upper.startswith('SUMMARY') or line_upper.startswith('**SUMMARY') or line_upper.startswith('## SUMMARY')):
                current_section = 'summary'
            elif 'KEY FINDINGS' in line_upper and ('KEY FINDINGS' in line_upper):
                current_section = 'key_findings'
            elif ('QUALITY ISSUES' in line_upper or 'DATA QUALITY' in line_upper) and 'ISSUES' in line_upper:
                current_section = 'quality_issues'
            elif 'RECOMMENDATIONS' in line_upper and ('RECOMMENDATIONS' in line_upper):
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section in ['key_findings', 'quality_issues', 'recommendations']:
                    sections[current_section].append(item)
            elif current_section == 'summary' and line:
                sections['summary'] += line + ' '
        
        sections['summary'] = sections['summary'].strip()
        return sections
