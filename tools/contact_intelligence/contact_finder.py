"""
Contact Finder - Search and generate contact information
"""
from common.llm.client import get_client
import re


class ContactFinder:
    """Find and generate business contact information"""
    
    def __init__(self):
        """Initialize contact finder"""
        self.client = get_client()
    
    def find_contact(self, company_name: str, role: str = None, 
                    industry: str = None, geography: str = None) -> dict:
        """
        Find contact information for a company/role
        
        Args:
            company_name: Company name or domain
            role: Job title or role (e.g., "VP of Sales")
            industry: Industry sector
            geography: Location/region
            
        Returns:
            Contact information with confidence scores
        """
        prompt = self._build_search_prompt(company_name, role, industry, geography)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business intelligence expert. Generate probable contact information with confidence reasoning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            contact_text = response.choices[0].message.content
            return self._parse_contact_info(contact_text, company_name)
            
        except Exception as e:
            return {
                'error': str(e),
                'contacts': [],
                'confidence_score': 0
            }
    
    def _build_search_prompt(self, company: str, role: str, industry: str, geography: str) -> str:
        """Build search prompt"""
        
        context = f"Company: {company}"
        if role:
            context += f"\nRole: {role}"
        if industry:
            context += f"\nIndustry: {industry}"
        if geography:
            context += f"\nGeography: {geography}"
        
        return f"""
Generate probable business contact information based on this search:

{context}

Please provide:

CONTACT INFORMATION:
- Name: [Probable name based on role/company]
- Title: [Job title]
- Email: [Generated email using common patterns]
- Phone: [If publicly available, otherwise mark as "Not Available"]
- LinkedIn: [Probable LinkedIn URL]

EMAIL PATTERN REASONING:
[Explain the email pattern used, e.g., firstname.lastname@company.com]

CONFIDENCE SCORE:
[0-100] - [Explanation of confidence level]

CONFIDENCE BREAKDOWN:
- Name Confidence: [0-100] - [Why]
- Email Confidence: [0-100] - [Why]
- Role Confidence: [0-100] - [Why]

SOURCE REFERENCES:
- [Source 1: Where this information might be found]
- [Source 2: Alternative sources]

VERIFICATION SUGGESTIONS:
- [Step 1: How to verify this contact]
- [Step 2: Alternative verification methods]

ALTERNATIVE CONTACTS:
- [Alternative 1: Other relevant contacts]
- [Alternative 2: Backup contacts]
"""
    
    def _parse_contact_info(self, text: str, company: str) -> dict:
        """Parse LLM contact response"""
        contact = {
            'company': company,
            'name': '',
            'title': '',
            'email': '',
            'phone': 'Not Available',
            'linkedin': '',
            'email_pattern': '',
            'confidence_score': 0,
            'confidence_breakdown': {},
            'sources': [],
            'verification_steps': [],
            'alternatives': []
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Extract contact info
            if line.startswith('- Name:') or line.startswith('Name:'):
                contact['name'] = line.split(':', 1)[-1].strip()
            elif line.startswith('- Title:') or line.startswith('Title:'):
                contact['title'] = line.split(':', 1)[-1].strip()
            elif line.startswith('- Email:') or line.startswith('Email:'):
                email = line.split(':', 1)[-1].strip()
                contact['email'] = email
            elif line.startswith('- Phone:') or line.startswith('Phone:'):
                contact['phone'] = line.split(':', 1)[-1].strip()
            elif line.startswith('- LinkedIn:') or line.startswith('LinkedIn:'):
                contact['linkedin'] = line.split(':', 1)[-1].strip()
            
            # Sections
            elif 'EMAIL PATTERN' in line.upper():
                current_section = 'pattern'
            elif 'CONFIDENCE SCORE:' in line.upper():
                current_section = 'score'
                # Extract score
                score_match = re.search(r'\[?(\d+)\]?', line)
                if score_match:
                    contact['confidence_score'] = int(score_match.group(1))
            elif 'CONFIDENCE BREAKDOWN:' in line.upper():
                current_section = 'breakdown'
            elif 'SOURCE REFERENCES:' in line.upper():
                current_section = 'sources'
            elif 'VERIFICATION' in line.upper():
                current_section = 'verification'
            elif 'ALTERNATIVE' in line.upper():
                current_section = 'alternatives'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section == 'sources':
                    contact['sources'].append(item)
                elif current_section == 'verification':
                    contact['verification_steps'].append(item)
                elif current_section == 'alternatives':
                    contact['alternatives'].append(item)
                elif current_section == 'breakdown' and ':' in item:
                    key, value = item.split(':', 1)
                    contact['confidence_breakdown'][key.strip()] = value.strip()
            elif current_section == 'pattern' and line:
                contact['email_pattern'] = line
        
        return contact
    
    def generate_email_variations(self, name: str, company_domain: str) -> list:
        """Generate common email pattern variations"""
        if not name or not company_domain:
            return []
        
        # Clean domain
        domain = company_domain.replace('www.', '').replace('http://', '').replace('https://', '')
        if '/' in domain:
            domain = domain.split('/')[0]
        
        # Parse name
        parts = name.lower().strip().split()
        if len(parts) < 2:
            return []
        
        first = parts[0]
        last = parts[-1]
        
        # Common patterns
        patterns = [
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{last}.{first}@{domain}",
            f"{first}@{domain}",
            f"{last}@{domain}"
        ]
        
        return patterns
