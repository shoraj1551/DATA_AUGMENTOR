"""
Policy Analyzer - Extract rules and coverage from policy documents
"""
from common.llm.client import get_client
import json
from config.settings import get_model_for_feature
from utils.safe_llm_parser import SafeLLMParser


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
                model=get_model_for_feature("insurance_claims"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an insurance policy expert. Extract and structure policy information clearly. Return strictly JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            analysis_text = response.choices[0].message.content
            # Use SafeLLMParser for robust JSON extraction
            return SafeLLMParser.parse_json(analysis_text, default={
                'coverage_rules': [],
                'exclusions': [],
                'loopholes': [],
                'claim_requirements': [],
                'contacts': {},
                'important_dates': {}
            })
            
        except Exception as e:
            return {
                'error': str(e),
                'coverage_rules': [],
                'exclusions': [],
                'contacts': {}
            }
    

    def is_insurance_policy(self, text: str) -> dict:
        """
        Check if the text is an insurance policy document.
        
        Args:
            text: Document text
            
        Returns:
            dict: {'is_policy': bool, 'reason': str}
        """
        # Truncate for quick check
        sample_text = text[:4000]
        
        try:
            response = self.client.chat.completions.create(
                model=get_model_for_feature("insurance_claims"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document classifier. Determine if the provided text is an insurance policy document. Return strictly JSON."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Classify this text. Is it an insurance policy or related document?
                        
                        TEXT:
                        {sample_text}
                        
                        Return JSON:
                        {{
                            "is_policy": boolean,
                            "reason": "concise explanation"
                        }}
                        """
                    }
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return SafeLLMParser.parse_json(result, default={'is_policy': False, 'reason': "Analysis failed"})
            
        except Exception as e:
            return {'is_policy': False, 'reason': f"Error: {str(e)}"}

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

Please provide a structured analysis in JSON format with the following keys:
- coverage_rules (list of strings)
- exclusions (list of strings)
- loopholes (list of strings)
- claim_requirements (list of strings)
- contacts (dictionary of contact info)
- important_dates (dictionary of dates)

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
    
    # Logic moved to SafeLLMParser.parse_json, manual _parse_analysis removed

