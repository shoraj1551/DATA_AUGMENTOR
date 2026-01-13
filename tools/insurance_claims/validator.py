"""
Claims Validator - Validate claims against policy rules
"""
from common.llm.client import get_client


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
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an insurance claims specialist. Validate claims thoroughly and provide clear guidance."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            validation_text = response.choices[0].message.content
            return self._parse_validation(validation_text)
            
        except Exception as e:
            return {
                'error': str(e),
                'is_valid': False,
                'issues': [],
                'next_steps': []
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

Please provide:

ELIGIBILITY STATUS:
[APPROVED / DENIED / NEEDS REVIEW]

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
    
    def _parse_validation(self, text: str) -> dict:
        """Parse validation response"""
        validation = {
            'eligibility_status': 'NEEDS REVIEW',
            'validation_results': [],
            'issues': [],
            'discrepancies': [],
            'next_steps': [],
            'approval_probability': 'Unknown'
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            if 'ELIGIBILITY STATUS:' in line.upper():
                current_section = 'status'
                # Extract status from same line or next
                if any(status in line.upper() for status in ['APPROVED', 'DENIED', 'NEEDS REVIEW']):
                    for status in ['APPROVED', 'DENIED', 'NEEDS REVIEW']:
                        if status in line.upper():
                            validation['eligibility_status'] = status
                            break
            elif 'VALIDATION RESULTS:' in line.upper():
                current_section = 'results'
            elif 'IDENTIFIED ISSUES:' in line.upper() or 'ISSUES:' in line.upper():
                current_section = 'issues'
            elif 'DISCREPANCIES:' in line.upper():
                current_section = 'discrepancies'
            elif 'NEXT STEPS' in line.upper():
                current_section = 'next_steps'
            elif 'APPROVAL PROBABILITY:' in line.upper() or 'ESTIMATED' in line.upper():
                current_section = 'probability'
                validation['approval_probability'] = line.split(':', 1)[-1].strip() if ':' in line else 'Unknown'
            elif line.startswith('-') or line.startswith('•') or line[0:2].replace('.', '').isdigit():
                item = line.lstrip('-•0123456789. ').strip()
                if current_section == 'results':
                    validation['validation_results'].append(item)
                elif current_section == 'issues':
                    validation['issues'].append(item)
                elif current_section == 'discrepancies':
                    validation['discrepancies'].append(item)
                elif current_section == 'next_steps':
                    validation['next_steps'].append(item)
        
        return validation
