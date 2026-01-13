"""
Rule Explainer - LLM-powered explanations for DQ rules
"""
from common.llm.client import get_client
import json


class RuleExplainer:
    """Generate human-readable explanations for DQ rules"""
    
    def __init__(self):
        """Initialize rule explainer"""
        self.client = get_client()
    
    def explain_rules(self, rules: list, schema_info: dict = None) -> dict:
        """
        Generate explanations for DQ rules
        
        Args:
            rules: List of generated DQ rules
            schema_info: Optional schema metadata
            
        Returns:
            Dictionary with explanations and recommendations
        """
        prompt = self._build_prompt(rules, schema_info)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data quality expert. Explain DQ rules in clear, business-friendly language."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            explanation_text = response.choices[0].message.content
            return self._parse_explanation(explanation_text)
            
        except Exception as e:
            return {
                'summary': 'Error generating explanations',
                'error': str(e),
                'rule_explanations': []
            }
    
    def _build_prompt(self, rules: list, schema_info: dict = None) -> str:
        """Build prompt for LLM"""
        rules_summary = []
        for rule in rules[:10]:  # Limit to first 10 for prompt size
            rules_summary.append({
                'column': rule['column'],
                'type': rule['rule_type'],
                'description': rule['description'],
                'severity': rule['severity']
            })
        
        return f"""
Explain these data quality rules in business-friendly language:

RULES:
{json.dumps(rules_summary, indent=2)}

Please provide:
1. **Summary**: Overall assessment of the DQ rules (2-3 sentences)
2. **Critical Rules**: Highlight the most important rules and why
3. **Implementation Priority**: Suggest order of implementation
4. **Business Impact**: Explain potential impact of rule failures

Format your response as:

SUMMARY:
[Your summary]

CRITICAL RULES:
- [Rule 1 and why it's critical]
- [Rule 2 and why it's critical]

IMPLEMENTATION PRIORITY:
1. [First priority]
2. [Second priority]
3. [Third priority]

BUSINESS IMPACT:
- [Impact 1]
- [Impact 2]
"""
    
    def _parse_explanation(self, text: str) -> dict:
        """Parse LLM response"""
        sections = {
            'summary': '',
            'critical_rules': [],
            'priority': [],
            'business_impact': []
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            if 'SUMMARY:' in line.upper():
                current_section = 'summary'
            elif 'CRITICAL RULES:' in line.upper():
                current_section = 'critical_rules'
            elif 'IMPLEMENTATION PRIORITY:' in line.upper() or 'PRIORITY:' in line.upper():
                current_section = 'priority'
            elif 'BUSINESS IMPACT:' in line.upper():
                current_section = 'business_impact'
            elif line.startswith('-') or line.startswith('•') or line[0:2].replace('.', '').isdigit():
                item = line.lstrip('-•0123456789. ').strip()
                if current_section in ['critical_rules', 'priority', 'business_impact']:
                    sections[current_section].append(item)
            elif current_section == 'summary' and line:
                sections['summary'] += line + ' '
        
        sections['summary'] = sections['summary'].strip()
        return sections
