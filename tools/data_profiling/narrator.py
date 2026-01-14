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
            from common.llm.client import call_with_fallback
            
            response = call_with_fallback(
                feature_name="data_profiling",
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
                "error": str(e),
                'executive_summary': '',
                'insights': [],
                'risks': [],
                'actions': []
            }
    
    def _build_prompt(self, profile: dict, anomalies: list, audience: str) -> str:
        """Build audience-specific prompt for narrative generation"""
        
        # Base context available to all audiences
        data_context = f"""
DATASET OVERVIEW:
- Rows: {profile['overview']['rows']:,}
- Columns: {profile['overview']['columns']}
- Missing Values: {profile['overview']['total_missing']}
- Duplicates: {profile['overview']['duplicate_rows']}

ANOMALIES DETECTED:
{json.dumps(anomalies[:5], indent=2)}
"""

        # 1. TECHNICAL AUDIENCE PROMPT
        if audience == 'technical':
            return f"""
{data_context}
- Memory Usage: {profile['overview']['memory_usage_mb']} MB

You are a Senior Data Engineer conducting a technical health check.
Generate a TECHNICAL narrative for Data Scientists/Engineers.

REQUIREMENTS:
1. FOCUS on data integrity, schema validation, outliers, and statistical anomalies.
2. USE technical terminology (e.g., skewness, cardinality, null density, type mismatch).
3. BE PRECISE and metric-heavy. Avoid business fluff.

Please provide:

EXECUTIVE SUMMARY:
[2-3 sentences on technical data health, schema validity, and readiness for modeling]

KEY INSIGHTS:
- [Insight 1: Statistical distribution highlight (e.g., skew, kurtosis)]
- [Insight 2: Data integrity observation (e.g., referential integrity hint, duplicates)]
- [Insight 3: Pattern or correlation note]

RISK ALERTS:
- [Risk 1: Technical data quality issue (e.g., mixed types, high nulls)]
- [Risk 2: Modeling risk (e.g., collinearity, class imbalance)]

RECOMMENDED ACTIONS:
1. [Data Ops: Specific cleaning step (e.g., "Impute column X with median")]
2. [Feature Eng: Transformation suggestion (e.g., "Log-transform column Y")]
3. [Infrastructure: Storage/Optimization tip]
"""

        # 2. EXECUTIVE AUDIENCE PROMPT
        elif audience == 'executive':
            return f"""
{data_context}

You are a Chief Data Officer reporting to the Board/CEO.
Generate an EXECUTIVE narrative.

REQUIREMENTS:
1. FOCUS on business health, strategic risk, ROI, and high-level trends.
2. USE plain business English. NO technical jargon (e.g., avoid "float64", "standard deviation").
3. LINK data state to business decision-making capability.

Please provide:

EXECUTIVE SUMMARY:
[2-3 sentences on what this data says about business performance or data asset value]

KEY INSIGHTS:
- [Insight 1: Major business trend or volume indicator]
- [Insight 2: High-level pattern affecting strategy]
- [Insight 3: Positive/Negative signal]

RISK ALERTS:
- [Risk 1: Strategic risk (e.g., "Incomplete customer data limits segmentation")]
- [Risk 2: Compliance/Governance concern]

RECOMMENDED ACTIONS:
1. [Strategy: High-level directive (e.g., "Invest in data collection for Region X")]
2. [Governance: Policy change]
3. [Investment: Resource allocation]
"""

        # 3. BUSINESS AUDIENCE PROMPT (Default)
        else:
            return f"""
{data_context}

You are a Business Analyst partnering with Product Managers and Operations.
Generate a BUSINESS/OPERATIONAL narrative.

REQUIREMENTS:
1. FOCUS on usability, customer segments, operational bottlenecks, and actionable patterns.
2. BALANCE business context with data evidence.
3. BE ACTIONABLE and operational.

Please provide:

EXECUTIVE SUMMARY:
[2-3 sentences on the "Usability" of this dataset for business operations]

KEY INSIGHTS:
- [Insight 1: Operational finding (e.g., "Most users are in segment X")]
- [Insight 2: Usability observation (e.g., "500 records missing emails")]
- [Insight 3: Interesting relationship]

RISK ALERTS:
- [Risk 1: Operational blocker (e.g., "Cannot contact 20% of users")]
- [Risk 2: Process gap]

RECOMMENDED ACTIONS:
1. [Operation: Immediate fix (e.g., "Run email enrichment campaign")]
2. [Process: Workflow update]
3. [Analysis: Follow-up question to ask]
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
            
            line_upper = line.upper()
            
            if 'EXECUTIVE SUMMARY' in line_upper:
                current_section = 'summary'
            elif 'KEY INSIGHTS' in line_upper or 'INSIGHTS' in line_upper and current_section != 'summary':
                current_section = 'insights'
            elif 'RISK ALERTS' in line_upper or 'RISKS' in line_upper:
                current_section = 'risks'
            elif 'RECOMMENDED ACTIONS' in line_upper or ('ACTIONS' in line_upper and 'RECOMMENDED' in line_upper):
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
