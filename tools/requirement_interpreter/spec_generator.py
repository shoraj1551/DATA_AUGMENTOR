"""
Spec Generator - LLM-powered specification generation
"""
from common.llm.client import get_client
import json


class SpecGenerator:
    """Generate analytical specifications using LLM"""
    
    def __init__(self):
        """Initialize spec generator"""
        self.client = get_client()
    
    def generate_spec(self, parsed_req: dict, glossary: dict = None, 
                     metrics_catalog: dict = None) -> dict:
        """
        Generate analytical specification
        
        Args:
            parsed_req: Parsed requirement from NLP parser
            glossary: Optional domain glossary
            metrics_catalog: Optional existing metrics catalog
            
        Returns:
            Complete analytical specification
        """
        prompt = self._build_prompt(parsed_req, glossary, metrics_catalog)
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst expert. Translate business requirements into precise analytical specifications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
            
            spec_text = response.choices[0].message.content
            return self._parse_spec(spec_text, parsed_req)
            
        except Exception as e:
            return {
                'error': str(e),
                'metric_definitions': [],
                'clarifying_questions': [],
                'sql_spec': ''
            }
    
    def _build_prompt(self, parsed_req: dict, glossary: dict = None, 
                     metrics_catalog: dict = None) -> str:
        """Build prompt for LLM"""
        
        glossary_text = ""
        if glossary:
            glossary_text = f"\nDOMAIN GLOSSARY:\n{json.dumps(glossary, indent=2)}\n"
        
        catalog_text = ""
        if metrics_catalog:
            catalog_text = f"\nEXISTING METRICS:\n{json.dumps(metrics_catalog, indent=2)}\n"
        
        return f"""
Translate this business requirement into a precise analytical specification:

BUSINESS REQUIREMENT:
"{parsed_req['original_text']}"

PARSED ENTITIES:
- Metrics: {', '.join(parsed_req['metrics']) if parsed_req['metrics'] else 'None detected'}
- Time Dimensions: {', '.join(parsed_req['time_dimensions']) if parsed_req['time_dimensions'] else 'None'}
- Filters: {', '.join(parsed_req['filters']) if parsed_req['filters'] else 'None'}
- Intent: {parsed_req['intent']}
{glossary_text}{catalog_text}

Please provide:

1. **METRIC DEFINITIONS**: Define each metric precisely
   - Metric name
   - Formula/calculation
   - Unit of measurement
   - Aggregation type (SUM, AVG, COUNT, etc.)

2. **GRAIN & FILTERS**: Specify data granularity
   - Time grain (daily, weekly, monthly, etc.)
   - Dimension grain (by product, by region, etc.)
   - Filter conditions

3. **CLARIFYING QUESTIONS**: List any ambiguities
   - What needs clarification?
   - Why is it important?

4. **SQL SPECIFICATION**: Provide SQL-ready structure
   - SELECT clause
   - FROM clause
   - WHERE clause
   - GROUP BY clause

Format your response as:

METRIC DEFINITIONS:
- [Metric 1]: [Definition]
- [Metric 2]: [Definition]

GRAIN & FILTERS:
- Time Grain: [grain]
- Dimension Grain: [dimensions]
- Filters: [conditions]

CLARIFYING QUESTIONS:
- [Question 1]
- [Question 2]

SQL SPECIFICATION:
```sql
[SQL query structure]
```

ASSUMPTIONS:
- [Assumption 1]
- [Assumption 2]
"""
    
    def _parse_spec(self, text: str, parsed_req: dict) -> dict:
        """Parse LLM response into structured spec"""
        spec = {
            'original_requirement': parsed_req['original_text'],
            'intent': parsed_req['intent'],
            'metric_definitions': [],
            'grain_and_filters': {},
            'clarifying_questions': [],
            'sql_spec': '',
            'assumptions': []
        }
        
        current_section = None
        sql_lines = []
        in_sql = False
        
        for line in text.split('\n'):
            line = line.strip()
            
            if 'METRIC DEFINITIONS:' in line.upper():
                current_section = 'metrics'
            elif 'GRAIN & FILTERS:' in line.upper() or 'GRAIN AND FILTERS:' in line.upper():
                current_section = 'grain'
            elif 'CLARIFYING QUESTIONS:' in line.upper():
                current_section = 'questions'
            elif 'SQL SPECIFICATION:' in line.upper():
                current_section = 'sql'
            elif 'ASSUMPTIONS:' in line.upper():
                current_section = 'assumptions'
            elif '```sql' in line.lower():
                in_sql = True
            elif '```' in line and in_sql:
                in_sql = False
            elif in_sql:
                sql_lines.append(line)
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section == 'metrics':
                    spec['metric_definitions'].append(item)
                elif current_section == 'questions':
                    spec['clarifying_questions'].append(item)
                elif current_section == 'assumptions':
                    spec['assumptions'].append(item)
                elif current_section == 'grain':
                    if ':' in item:
                        key, value = item.split(':', 1)
                        spec['grain_and_filters'][key.strip()] = value.strip()
        
        spec['sql_spec'] = '\n'.join(sql_lines)
        return spec
