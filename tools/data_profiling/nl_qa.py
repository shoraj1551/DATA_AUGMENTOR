"""
Natural Language Q&A for Data Profiling with RAG Architecture
Allows executives to ask questions about their data in natural language
Uses Retrieval-Augmented Generation for accurate, grounded answers
"""
import pandas as pd
import json
import numpy as np
from common.llm.client import call_with_fallback


class NaturalLanguageQA:
    """Process natural language questions about datasets using RAG"""
    
    def __init__(self, df: pd.DataFrame, profile: dict):
        """
        Initialize NL Q&A processor with RAG
        
        Args:
            df: DataFrame to query
            profile: Dataset profile dictionary
        """
        self.df = df
        self.profile = profile
        self._build_knowledge_base()
        
    def _build_knowledge_base(self):
        """Build knowledge base from dataset for RAG retrieval"""
        self.knowledge_base = []
        
        # 1. Add column-level information
        for col in self.profile['columns']:
            col_info = {
                'type': 'column_info',
                'content': f"Column '{col['name']}' is of type {col.get('dtype', 'unknown')} with {col['unique']} unique values, {col['missing']} missing values ({(col['missing']/self.profile['overview']['rows']*100):.1f}%)",
                'metadata': {
                    'column': col['name'],
                    'dtype': col.get('dtype'),
                    'unique': col['unique'],
                    'missing': col['missing']
                }
            }
            self.knowledge_base.append(col_info)
        
        # 2. Add statistical summaries for numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            try:
                stats = {
                    'type': 'statistics',
                    'content': f"Column '{col}' statistics: min={self.df[col].min():.2f}, max={self.df[col].max():.2f}, mean={self.df[col].mean():.2f}, median={self.df[col].median():.2f}",
                    'metadata': {
                        'column': col,
                        'min': float(self.df[col].min()),
                        'max': float(self.df[col].max()),
                        'mean': float(self.df[col].mean()),
                        'median': float(self.df[col].median())
                    }
                }
                self.knowledge_base.append(stats)
            except Exception:
                continue
        
        # 3. Add top values for categorical columns
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols[:5]:  # Top 5 categorical columns
            try:
                if self.df[col].nunique() < 20:
                    top_values = self.df[col].value_counts().head(5)
                    values_str = ", ".join([f"{val} ({count})" for val, count in top_values.items()])
                    cat_info = {
                        'type': 'categorical_values',
                        'content': f"Column '{col}' top values: {values_str}",
                        'metadata': {
                            'column': col,
                            'top_values': top_values.to_dict()
                        }
                    }
                    self.knowledge_base.append(cat_info)
            except Exception:
                continue
        
        # 4. Add overall dataset info
        overview = {
            'type': 'overview',
            'content': f"Dataset has {self.profile['overview']['rows']:,} rows and {self.profile['overview']['columns']} columns, with {self.profile['overview']['total_missing']:,} total missing values and {self.profile['overview']['duplicate_rows']} duplicate rows",
            'metadata': self.profile['overview']
        }
        self.knowledge_base.append(overview)
    
    def _retrieve_relevant_context(self, question: str, top_k: int = 5) -> str:
        """
        Retrieve relevant context from knowledge base (simple keyword matching)
        In production, this would use vector embeddings
        
        Args:
            question: User question
            top_k: Number of top contexts to retrieve
            
        Returns:
            Relevant context string
        """
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        question_lower = question.lower()
        
        # Score each knowledge item by keyword overlap
        scored_items = []
        for item in self.knowledge_base:
            content_lower = item['content'].lower()
            
            # Count keyword matches
            score = 0
            for word in question_lower.split():
                if len(word) > 3 and word in content_lower:
                    score += 1
            
            # Boost score for column names mentioned
            if 'column' in item.get('metadata', {}):
                col_name = item['metadata']['column'].lower()
                if col_name in question_lower:
                    score += 5
            
            scored_items.append((score, item))
        
        # Sort by score and get top_k
        scored_items.sort(key=lambda x: x[0], reverse=True)
        top_items = [item for score, item in scored_items[:top_k] if score > 0]
        
        # Build context string
        if not top_items:
            # Return general overview if no specific match
            top_items = [item for item in self.knowledge_base if item['type'] == 'overview']
        
        context = "\n".join([item['content'] for item in top_items])
        return context
    
    def ask(self, question: str) -> dict:
        """
        Process a natural language question using RAG
        
        Args:
            question: Natural language question
            
        Returns:
            dict with answer, data, visualization info, and download option
        """
        # RETRIEVAL: Get relevant context from knowledge base
        relevant_context = self._retrieve_relevant_context(question)
        
        # AUGMENTATION: Build enhanced prompt with context
        enhanced_prompt = f"""**Retrieved Context:**
{relevant_context}

**Dataset Overview:**
- Rows: {self.profile['overview']['rows']:,}
- Columns: {self.profile['overview']['columns']}
- Missing Values: {self.profile['overview']['total_missing']:,}
- Duplicates: {self.profile['overview']['duplicate_rows']}

**User Question:** {question}

Based on the retrieved context and dataset overview above, provide a clear, accurate answer."""
        
        # GENERATION: Get LLM to interpret and generate response
        try:
            response = call_with_fallback(
                feature_name="data_profiling",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a data analyst assistant using RAG (Retrieval-Augmented Generation).
                        
IMPORTANT: Base your answers ONLY on the retrieved context provided. Do not make up information.

When answering:
- Use specific numbers from the context
- Use bullet points for lists
- Highlight key findings
- Suggest actions when relevant
- If context doesn't have the answer, say so

Response format (JSON):
{
    "answer": "Clear text answer based on context",
    "query_type": "summary|filter|aggregate|comparison|recommendation",
    "needs_data": true/false,
    "pandas_code": "df.head()" (if needs_data is true),
    "visualization": "none|table|chart",
    "confidence": "high|medium|low" (based on context relevance)
}"""
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.2  # Lower temperature for more factual responses
            )
            
            # Parse LLM response
            result = self._parse_response(response.choices[0].message.content, question)
            
            # Execute pandas code if needed
            if result.get('needs_data') and result.get('pandas_code'):
                try:
                    # Execute the pandas code safely
                    exec_result = eval(result['pandas_code'], {'df': self.df, 'pd': pd, 'np': np})
                    result['data'] = exec_result
                    result['downloadable'] = True
                except Exception as e:
                    result['data_error'] = str(e)
                    result['downloadable'] = False
            else:
                result['downloadable'] = False
            
            # Add context used for transparency
            result['context_used'] = relevant_context
            
            return result
            
        except Exception as e:
            return {
                'answer': f"I encountered an error processing your question: {str(e)}",
                'query_type': 'error',
                'needs_data': False,
                'downloadable': False
            }
    
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
                    'visualization': 'none',
                    'confidence': 'medium'
                }
            
            result = json.loads(json_str)
            return result
            
        except Exception:
            # Fallback: return text as answer
            return {
                'answer': response_text,
                'query_type': 'summary',
                'needs_data': False,
                'visualization': 'none',
                'confidence': 'low'
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
