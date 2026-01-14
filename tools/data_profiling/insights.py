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
                use_case="data_profiling",
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
        """Build prompt for LLM"""
        return f"""
Analyze this dataset profile and provide insights:

DATASET OVERVIEW:
- Rows: {profile['overview']['rows']}
- Columns: {profile['overview']['columns']}
- Memory: {profile['overview']['memory_usage_mb']} MB
- Duplicates: {profile['overview']['duplicate_rows']}
- Missing Values: {profile['overview']['total_missing']}

ANOMALIES DETECTED:
{json.dumps(anomalies, indent=2)}

MISSING DATA:
{json.dumps(profile['missing_data'], indent=2)}

Please provide:
1. **Summary**: 2-3 sentence overview of the dataset quality
2. **Key Findings**: 3-5 bullet points of important observations
3. **Data Quality Issues**: List any problems found
4. **Recommendations**: 3-5 actionable next steps

Format your response as:

SUMMARY:
[Your summary here]

KEY FINDINGS:
- [Finding 1]
- [Finding 2]
- [Finding 3]

DATA QUALITY ISSUES:
- [Issue 1]
- [Issue 2]

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]
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
