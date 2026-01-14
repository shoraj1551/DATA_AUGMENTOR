"""
Natural Language Q&A for Data Profiling
Allows executives to ask questions about their data in natural language
"""
import pandas as pd
import json
from common.llm.client import call_with_fallback


class NaturalLanguageQA:
    """Process natural language questions about datasets"""
    
    def __init__(self, df: pd.DataFrame, profile: dict):
        """
        Initialize NL Q&A processor
        
        Args:
            df: DataFrame to query
            profile: Dataset profile dictionary
        """
        self.df = df
        self.profile = profile
        
    def ask(self, question: str) -> dict:
        """
        Process a natural language question
        
        Args:
            question: Natural language question
            
        Returns:
            dict with answer, data, and visualization info
        """
        # Build context about the dataset
        context = self._build_context()
        
        # Get LLM to interpret the question and generate response
        try:
            response = call_with_fallback(
                feature_name="data_profiling",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a data analyst assistant. Answer questions about datasets clearly and concisely.
                        
When answering:
- Be specific with numbers
- Use bullet points for lists
- Highlight key findings
- Suggest actions when relevant

Response format (JSON):
{
    "answer": "Clear text answer",
    "query_type": "summary|filter|aggregate|comparison|recommendation",
    "needs_data": true/false,
    "pandas_code": "df.head()" (if needs_data is true),
    "visualization": "none|table|chart" (suggest visualization type)
}"""
                    },
                    {
                        "role": "user",
                        "content": f"""Dataset Context:
{context}

Question: {question}

Provide a helpful answer based on the dataset profile."""
                    }
                ],
                temperature=0.3
            )
            
            # Parse LLM response
            result = self._parse_response(response.choices[0].message.content, question)
            
            # Execute pandas code if needed
            if result.get('needs_data') and result.get('pandas_code'):
                try:
                    # Execute the pandas code safely
                    exec_result = eval(result['pandas_code'], {'df': self.df, 'pd': pd})
                    result['data'] = exec_result
                except Exception as e:
                    result['data_error'] = str(e)
            
            return result
            
        except Exception as e:
            return {
                'answer': f"I encountered an error processing your question: {str(e)}",
                'query_type': 'error',
                'needs_data': False
            }
    
    def _build_context(self) -> str:
        """Build context string about the dataset"""
        context_parts = []
        
        # Basic info
        context_parts.append(f"**Dataset Overview:**")
        context_parts.append(f"- Rows: {self.profile['overview']['rows']:,}")
        context_parts.append(f"- Columns: {self.profile['overview']['columns']}")
        context_parts.append(f"- Missing Values: {self.profile['overview']['total_missing']:,}")
        context_parts.append(f"- Duplicates: {self.profile['overview']['duplicate_rows']}")
        
        # Column names and types
        context_parts.append(f"\n**Columns:**")
        for col in self.profile['columns'][:10]:  # First 10 columns
            context_parts.append(f"- {col['name']} ({col.get('dtype', 'unknown')})")
        
        if len(self.profile['columns']) > 10:
            context_parts.append(f"... and {len(self.profile['columns']) - 10} more columns")
        
        return "\n".join(context_parts)
    
    def _parse_response(self, response_text: str, question: str) -> dict:
        """Parse LLM response"""
        try:
            # Try to extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_str = response_text[json_start:json_end].strip()
            elif '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
            else:
                # No JSON found, treat entire response as answer
                return {
                    'answer': response_text,
                    'query_type': 'summary',
                    'needs_data': False,
                    'visualization': 'none'
                }
            
            result = json.loads(json_str)
            return result
            
        except Exception:
            # Fallback: return text as answer
            return {
                'answer': response_text,
                'query_type': 'summary',
                'needs_data': False,
                'visualization': 'none'
            }
    
    def get_suggested_questions(self) -> list:
        """Get suggested questions based on dataset"""
        suggestions = [
            "What's the overall data quality?",
            "What are the top 3 data quality issues?",
            "Which columns have the most missing values?",
            "Show me a summary of this dataset",
            "What should I fix first?",
        ]
        
        # Add column-specific suggestions
        if self.profile['overview']['duplicate_rows'] > 0:
            suggestions.append("How many duplicate records are there?")
        
        if self.profile['overview']['total_missing'] > 0:
            suggestions.append("Which records have missing values?")
        
        return suggestions[:6]  # Return top 6
