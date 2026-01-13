"""
Policy Analyzer - Extract rules and coverage from policy documents
"""
from common.llm.client import get_client
import json


class PolicyAnalyzer:
    """Analyze insurance policy documents"""
    
    def __init__(self):
        """Initialize policy analyzer"""
        self.client = get_client()
    
    def analyze_policy(self, policy_text: str) -> dict:
        """
        Analyze policy document and extract key information
        
        Args:
            policy_text: Full policy document text
            
        Returns:
            Structured policy analysis
        """
        prompt = self._build_analysis_prompt(policy_text)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an insurance policy expert. Extract and structure policy information clearly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis(analysis_text)
            
        except Exception as e:
            return {
                'error': str(e),
                'coverage_rules': [],
                'exclusions': [],
                'contacts': {}
            }
    
    def _build_analysis_prompt(self, policy_text: str) -> str:
        """Build prompt for policy analysis"""
        # Truncate if too long
        max_length = 8000
        if len(policy_text) > max_length:
            policy_text = policy_text[:max_length] + "... [truncated]"
        
        return f"""
Analyze this insurance policy document and extract key information:

POLICY DOCUMENT:
{policy_text}

Please provide a structured analysis:

COVERAGE RULES:
- [Rule 1: What is covered and conditions]
- [Rule 2: Coverage limits and amounts]
- [Rule 3: Eligibility requirements]

EXCLUSIONS & LIMITATIONS:
- [Exclusion 1: What is NOT covered]
- [Exclusion 2: Limitations and restrictions]

LOOPHOLES & AMBIGUITIES:
- [Loophole 1: Unclear language or gaps]
- [Loophole 2: Potential interpretation issues]

CLAIM REQUIREMENTS:
- [Requirement 1: Documents needed]
- [Requirement 2: Timelines and deadlines]
- [Requirement 3: Submission process]

KEY CONTACTS:
- Claims Department: [Contact info]
- Customer Service: [Contact info]
- Emergency: [Contact info]

IMPORTANT DATES:
- Policy Start: [Date]
- Policy End: [Date]
- Renewal: [Date]
"""
    
    def _parse_analysis(self, text: str) -> dict:
        """Parse LLM analysis response"""
        analysis = {
            'coverage_rules': [],
            'exclusions': [],
            'loopholes': [],
            'claim_requirements': [],
            'contacts': {},
            'important_dates': {}
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            if 'COVERAGE RULES:' in line.upper():
                current_section = 'coverage_rules'
            elif 'EXCLUSIONS' in line.upper() or 'LIMITATIONS:' in line.upper():
                current_section = 'exclusions'
            elif 'LOOPHOLES' in line.upper() or 'AMBIGUITIES:' in line.upper():
                current_section = 'loopholes'
            elif 'CLAIM REQUIREMENTS:' in line.upper():
                current_section = 'claim_requirements'
            elif 'KEY CONTACTS:' in line.upper():
                current_section = 'contacts'
            elif 'IMPORTANT DATES:' in line.upper():
                current_section = 'dates'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section in ['coverage_rules', 'exclusions', 'loopholes', 'claim_requirements']:
                    analysis[current_section].append(item)
                elif current_section == 'contacts' and ':' in item:
                    key, value = item.split(':', 1)
                    analysis['contacts'][key.strip()] = value.strip()
                elif current_section == 'dates' and ':' in item:
                    key, value = item.split(':', 1)
                    analysis['important_dates'][key.strip()] = value.strip()
        
        return analysis
