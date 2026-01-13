"""
Confidence Scorer - Score and explain contact confidence
"""
from common.llm.client import get_client


class ConfidenceScorer:
    """Score contact information confidence"""
    
    def __init__(self):
        """Initialize confidence scorer"""
        self.client = get_client()
    
    def score_contact(self, contact_info: dict) -> dict:
        """
        Score contact confidence with detailed reasoning
        
        Args:
            contact_info: Contact information to score
            
        Returns:
            Confidence analysis with reasoning
        """
        prompt = self._build_scoring_prompt(contact_info)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data quality expert. Score contact information confidence with clear reasoning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            scoring_text = response.choices[0].message.content
            return self._parse_scoring(scoring_text)
            
        except Exception as e:
            return {
                'error': str(e),
                'overall_score': 0,
                'reasoning': ''
            }
    
    def _build_scoring_prompt(self, contact: dict) -> str:
        """Build scoring prompt"""
        import json
        
        return f"""
Score the confidence level of this contact information:

CONTACT DATA:
{json.dumps(contact, indent=2)}

Please provide a detailed confidence analysis:

OVERALL CONFIDENCE SCORE:
[0-100]

SCORING BREAKDOWN:
- Data Completeness: [0-100] - [How complete is the information]
- Email Validity: [0-100] - [How likely is the email correct]
- Role Accuracy: [0-100] - [How accurate is the role/title]
- Source Reliability: [0-100] - [How reliable are the sources]

CONFIDENCE REASONING:
[Detailed explanation of why this score was assigned]

RED FLAGS:
- [Flag 1: Any concerns or issues]
- [Flag 2: Missing information]

GREEN FLAGS:
- [Flag 1: Positive indicators]
- [Flag 2: Strong confidence factors]

IMPROVEMENT SUGGESTIONS:
- [Suggestion 1: How to increase confidence]
- [Suggestion 2: Additional verification steps]
"""
    
    def _parse_scoring(self, text: str) -> dict:
        """Parse scoring response"""
        import re
        
        scoring = {
            'overall_score': 0,
            'breakdown': {},
            'reasoning': '',
            'red_flags': [],
            'green_flags': [],
            'improvements': []
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            if 'OVERALL CONFIDENCE SCORE:' in line.upper():
                current_section = 'score'
                score_match = re.search(r'\[?(\d+)\]?', line)
                if score_match:
                    scoring['overall_score'] = int(score_match.group(1))
            elif 'SCORING BREAKDOWN:' in line.upper():
                current_section = 'breakdown'
            elif 'CONFIDENCE REASONING:' in line.upper():
                current_section = 'reasoning'
            elif 'RED FLAGS:' in line.upper():
                current_section = 'red_flags'
            elif 'GREEN FLAGS:' in line.upper():
                current_section = 'green_flags'
            elif 'IMPROVEMENT' in line.upper():
                current_section = 'improvements'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section == 'breakdown' and ':' in item:
                    key, value = item.split(':', 1)
                    scoring['breakdown'][key.strip()] = value.strip()
                elif current_section == 'red_flags':
                    scoring['red_flags'].append(item)
                elif current_section == 'green_flags':
                    scoring['green_flags'].append(item)
                elif current_section == 'improvements':
                    scoring['improvements'].append(item)
            elif current_section == 'reasoning' and line:
                scoring['reasoning'] += line + ' '
        
        scoring['reasoning'] = scoring['reasoning'].strip()
        return scoring
