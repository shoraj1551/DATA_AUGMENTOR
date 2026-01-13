"""
QA Interface - LLM-powered question answering
"""
from common.llm.client import get_client
import json


class QAInterface:
    """Natural language QA over knowledge base"""
    
    def __init__(self):
        """Initialize QA interface"""
        self.client = get_client()
    
    def answer_question(self, question: str, context_entries: list) -> dict:
        """
        Answer question using knowledge base context
        
        Args:
            question: User question
            context_entries: Relevant KB entries
            
        Returns:
            Answer with sources
        """
        prompt = self._build_prompt(question, context_entries)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful project assistant. Answer questions using the provided knowledge base context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            answer_text = response.choices[0].message.content
            return {
                'question': question,
                'answer': answer_text,
                'sources': [e.get('id') for e in context_entries],
                'context_count': len(context_entries)
            }
            
        except Exception as e:
            return {
                'question': question,
                'answer': f'Error generating answer: {str(e)}',
                'sources': [],
                'error': str(e)
            }
    
    def _build_prompt(self, question: str, context_entries: list) -> str:
        """Build prompt for QA"""
        
        context_text = ""
        for i, entry in enumerate(context_entries[:5], 1):  # Limit to 5 most relevant
            context_text += f"\n[Entry {i}] ({entry.get('category', 'unknown')})\n"
            context_text += f"{entry.get('content', '')}\n"
            if entry.get('tags'):
                context_text += f"Tags: {', '.join(entry.get('tags', []))}\n"
        
        return f"""
Answer the following question using the knowledge base context provided.

QUESTION:
{question}

KNOWLEDGE BASE CONTEXT:
{context_text}

Please provide:
1. A clear, direct answer to the question
2. Reference specific entries when applicable
3. If the context doesn't contain enough information, say so

ANSWER:
"""
    
    def generate_onboarding_guide(self, entries: list, focus_area: str = None) -> str:
        """
        Generate onboarding guide from knowledge base
        
        Args:
            entries: KB entries
            focus_area: Optional focus area
            
        Returns:
            Onboarding guide text
        """
        prompt = f"""
Create an onboarding guide using this project knowledge:

{json.dumps([{
    'category': e.get('category'),
    'content': e.get('content')[:200],  # Truncate for prompt size
    'tags': e.get('tags', [])
} for e in entries[:20]], indent=2)}

Focus Area: {focus_area or 'General'}

Create a structured onboarding guide with:
1. Project Overview
2. Key Concepts
3. Important Decisions
4. Getting Started Steps
5. Common Patterns
"""
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {"role": "system", "content": "You are a technical writer creating onboarding documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating guide: {str(e)}"
