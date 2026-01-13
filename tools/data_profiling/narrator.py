"""
Insight Narrator - Convert data to audience-aware narratives
"""
from common.llm.client import get_client
import json


class InsightNarrator:
    """Generate clear narratives from data analysis results"""
    
    def __init__(self):
        """Initialize narrator"""
        self.client = get_client()
    
    def generate_narrative(self, profile: dict, anomalies: list, 
                          audience: str = 'technical') -> dict:
        """
        Generate narrative from profiling results
        
        Args:
            profile: Dataset profile
            anomalies: Detected anomalies
            audience: Target audience (executive, technical, business)
            
        Returns:
            Narrative with insights and recommendations
        """
        prompt = self._build_prompt(profile, anomalies, audience)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a data storyteller. Create clear, {audience}-friendly narratives from data analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4
            )
            
            narrative_text = response.choices[0].message.content
            return self._parse_narrative(narrative_text)
            
        except Exception as e:
            return {
                'error': str(e),
                'executive_summary': '',
                'insights': [],
                'risks': [],
                'actions': []
            }
    
    def _build_prompt(self, profile: dict, anomalies: list, audience: str) -> str:
        """Build prompt for narrative generation"""
        
        audience_guidance = {
            'executive': 'Focus on business impact, high-level insights, and strategic recommendations. Avoid technical jargon.',
            'technical': 'Include technical details, statistical measures, and implementation specifics.',
            'business': 'Balance business context with data insights. Use clear language with some technical terms explained.'
        }
        
        return f"""
Create a {audience}-friendly narrative from this data analysis:

DATASET OVERVIEW:
- Rows: {profile['overview']['rows']:,}
- Columns: {profile['overview']['columns']}
- Missing Values: {profile['overview']['total_missing']}
- Duplicates: {profile['overview']['duplicate_rows']}

ANOMALIES:
{json.dumps(anomalies[:5], indent=2)}

AUDIENCE: {audience.upper()}
{audience_guidance.get(audience, '')}

Please provide:

EXECUTIVE SUMMARY:
[2-3 sentences summarizing the data quality and key findings]

KEY INSIGHTS:
- [Insight 1: What the data tells us]
- [Insight 2: Important patterns or trends]
- [Insight 3: Notable observations]

RISK ALERTS:
- [Risk 1: Potential data quality issues]
- [Risk 2: Business impact concerns]

RECOMMENDED ACTIONS:
1. [Action 1: Immediate steps]
2. [Action 2: Short-term improvements]
3. [Action 3: Long-term strategy]
"""
    
    def _parse_narrative(self, text: str) -> dict:
        """Parse LLM narrative response"""
        narrative = {
            'executive_summary': '',
            'insights': [],
            'risks': [],
            'actions': []
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            if 'EXECUTIVE SUMMARY:' in line.upper():
                current_section = 'summary'
            elif 'KEY INSIGHTS:' in line.upper() or 'INSIGHTS:' in line.upper():
                current_section = 'insights'
            elif 'RISK ALERTS:' in line.upper() or 'RISKS:' in line.upper():
                current_section = 'risks'
            elif 'RECOMMENDED ACTIONS:' in line.upper() or 'ACTIONS:' in line.upper():
                current_section = 'actions'
            elif line.startswith('-') or line.startswith('•') or line[0:2].replace('.', '').isdigit():
                item = line.lstrip('-•0123456789. ').strip()
                if current_section == 'insights':
                    narrative['insights'].append(item)
                elif current_section == 'risks':
                    narrative['risks'].append(item)
                elif current_section == 'actions':
                    narrative['actions'].append(item)
            elif current_section == 'summary' and line:
                narrative['executive_summary'] += line + ' '
        
        narrative['executive_summary'] = narrative['executive_summary'].strip()
        return narrative
