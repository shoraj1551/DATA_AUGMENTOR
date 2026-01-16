"""
Claims Validator - Validate claims against policy rules
"""
from common.llm.client import get_client
import json
from config.settings import get_model_for_feature
from utils.safe_llm_parser import SafeLLMParser


class ClaimsValidator:
    """Validate insurance claims"""
    
    def __init__(self):
        """Initialize claims validator"""
        self.client = get_client()
    
    def validate_claim(self, claim_details: dict, policy_analysis: dict) -> dict:
        """
        Validate a claim against policy rules
        
        Args:
            claim_details: Claim information
            policy_analysis: Analyzed policy rules
            
        Returns:
            Validation results with recommendations
        """
        prompt = self._build_validation_prompt(claim_details, policy_analysis)
        
        try:
            response = self.client.chat.completions.create(
                model=get_model_for_feature("insurance_claims"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an insurance claims specialist. Validate claims thoroughly and provide clear guidance. Return strictly JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            validation_text = response.choices[0].message.content
            # Use SafeLLMParser for robust JSON extraction
            return SafeLLMParser.parse_json(validation_text, default={
                'eligibility_status': 'NEEDS REVIEW',
                'validation_results': [],
                'issues': [],
                'discrepancies': [],
                'next_steps': [],
                'approval_probability': 'Unknown'
            })
            
        except Exception as e:
            return {
                'error': str(e),
                'is_valid': False,
                'issues': [],
                'next_steps': []
            }
    

    def generate_claim_checklist(self, topic: str, policy_analysis: dict) -> dict:
        """
        Generate a checklist of requirements and steps for a specific claim topic.
        
        Args:
            topic: User's claim topic (e.g. "Knee Surgery", "Lost Luggage")
            policy_analysis: Analyzed policy rules
            
        Returns:
            dict: { 'required_documents': [], 'steps': [], 'critical_warnings': [] }
        """
        # Create a focused prompt
        prompt = f"""
        User wants to file a claim for: "{topic}"
        
        Based ONLY on the policy details below, provide a practical checklist.
        
        POLICY RULES:
        {json.dumps(policy_analysis.get('coverage_rules', []), indent=2)}
        
        EXCLUSIONS:
        {json.dumps(policy_analysis.get('exclusions', []), indent=2)}
        
        REQUIREMENTS:
        {json.dumps(policy_analysis.get('claim_requirements', []), indent=2)}
        
        Return JSON with:
        - required_documents (list of strings): Specific docs needed (e.g. "Itemized bill", "Police report").
        - steps (list of strings): Step-by-step generic process based on policy type.
        - critical_warnings (list of strings): Any exclusions or deadlines relevant to THIS specific topic.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=get_model_for_feature("insurance_claims"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an insurance guide. valid claims. Return strictly JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content
            return SafeLLMParser.parse_json(result_text, default={
                'required_documents': ["Policy Document", "ID Proof"],
                'steps': ["Contact Insurer"],
                'critical_warnings': []
            })
            
        except Exception as e:
            return {
                'error': str(e),
                'required_documents': [],
                'steps': []
            }

    def _build_validation_prompt(self, claim_details: dict, policy_analysis: dict) -> str:
        """Build validation prompt"""
        import json
        
        return f"""
Validate this insurance claim against the policy rules:

CLAIM DETAILS:
{json.dumps(claim_details, indent=2)}

POLICY COVERAGE RULES:
{json.dumps(policy_analysis.get('coverage_rules', []), indent=2)}

POLICY EXCLUSIONS:
{json.dumps(policy_analysis.get('exclusions', []), indent=2)}

CLAIM REQUIREMENTS:
{json.dumps(policy_analysis.get('claim_requirements', []), indent=2)}

Please provide a structured validation in JSON format with the following keys:
- eligibility_status (string: APPROVED, DENIED, or NEEDS REVIEW)
- validation_results (list of strings)
- issues (list of strings)
- discrepancies (list of strings)
- next_steps (list of strings)
- approval_probability (string)

VALIDATION RESULTS:
- [Check 1: Coverage verification]
- [Check 2: Exclusion check]
- [Check 3: Documentation check]

IDENTIFIED ISSUES:
- [Issue 1: Missing documents or information]
- [Issue 2: Coverage gaps or exclusions]

DISCREPANCIES:
- [Discrepancy 1: Mismatches between claim and policy]

NEXT STEPS FOR USER:
1. [Step 1: What user needs to do]
2. [Step 2: Documents to gather]
3. [Step 3: How to submit]

ESTIMATED APPROVAL PROBABILITY:
[High / Medium / Low] - [Reason]
"""
