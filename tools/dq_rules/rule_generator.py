"""
Rule Generator - Generate DQ rules from patterns
"""
from typing import Dict, List, Any


class RuleGenerator:
    """Generate data quality rules from detected patterns"""
    
    def __init__(self):
        """Initialize rule generator"""
        pass
    
    def generate_rules(self, patterns: Dict[str, List[Dict[str, Any]]], 
                      criticality: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Generate DQ rules from patterns
        
        Args:
            patterns: Detected patterns by column
            criticality: Business criticality by column (high/medium/low)
            
        Returns:
            List of DQ rules
        """
        rules = []
        criticality = criticality or {}
        
        for col, col_patterns in patterns.items():
            col_criticality = criticality.get(col, 'medium')
            
            for pattern in col_patterns:
                rule = self._pattern_to_rule(col, pattern, col_criticality)
                if rule:
                    rules.append(rule)
        
        return rules
    
    def _pattern_to_rule(self, col: str, pattern: Dict[str, Any], 
                        criticality: str) -> Dict[str, Any]:
        """Convert a pattern to a DQ rule"""
        
        rule_type = pattern['type']
        
        if rule_type == 'null_check':
            return {
                'column': col,
                'rule_type': 'not_null',
                'severity': self._adjust_severity(pattern['severity'], criticality),
                'description': f'{col} should not contain null values',
                'validation_code': f"df['{col}'].notnull().all()",
                'failure_message': f'{col} contains null values: {{count}} nulls found'
            }
        
        elif rule_type == 'type_check':
            return {
                'column': col,
                'rule_type': 'type_validation',
                'severity': 'high',
                'description': f'{col} must be of type {pattern["detail"]}',
                'validation_code': f"df['{col}'].dtype == '{pattern['detail']}'",
                'failure_message': f'{col} has incorrect data type'
            }
        
        elif rule_type == 'range_check':
            return {
                'column': col,
                'rule_type': 'range_validation',
                'severity': self._adjust_severity(pattern['severity'], criticality),
                'description': f'{col} must be between {pattern["min"]} and {pattern["max"]}',
                'validation_code': f"df['{col}'].between({pattern['min']}, {pattern['max']}).all()",
                'failure_message': f'{col} contains values outside range [{pattern["min"]}, {pattern["max"]}]',
                'min': pattern['min'],
                'max': pattern['max']
            }
        
        elif rule_type == 'length_check':
            return {
                'column': col,
                'rule_type': 'length_validation',
                'severity': 'medium',
                'description': f'{col} length must be between {pattern["min_length"]} and {pattern["max_length"]}',
                'validation_code': f"df['{col}'].str.len().between({pattern['min_length']}, {pattern['max_length']}).all()",
                'failure_message': f'{col} contains values with invalid length',
                'min_length': pattern['min_length'],
                'max_length': pattern['max_length']
            }
        
        elif rule_type == 'format_check':
            format_type = pattern.get('format', 'unknown')
            if format_type == 'email':
                return {
                    'column': col,
                    'rule_type': 'format_validation',
                    'severity': 'high',
                    'description': f'{col} must be valid email format',
                    'validation_code': f"df['{col}'].str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$').all()",
                    'failure_message': f'{col} contains invalid email addresses',
                    'format': 'email'
                }
        
        elif rule_type == 'uniqueness':
            return {
                'column': col,
                'rule_type': 'uniqueness_validation',
                'severity': 'high',
                'description': f'{col} values must be unique',
                'validation_code': f"df['{col}'].is_unique",
                'failure_message': f'{col} contains duplicate values'
            }
        
        elif rule_type == 'cardinality_check':
            allowed = pattern.get('allowed_values', [])
            return {
                'column': col,
                'rule_type': 'cardinality_validation',
                'severity': 'medium',
                'description': f'{col} must be one of allowed values',
                'validation_code': f"df['{col}'].isin({allowed}).all()",
                'failure_message': f'{col} contains values not in allowed set',
                'allowed_values': allowed
            }
        
        return None
    
    def _adjust_severity(self, pattern_severity: str, criticality: str) -> str:
        """Adjust severity based on business criticality"""
        severity_map = {
            ('high', 'high'): 'critical',
            ('high', 'medium'): 'high',
            ('high', 'low'): 'medium',
            ('medium', 'high'): 'high',
            ('medium', 'medium'): 'medium',
            ('medium', 'low'): 'low',
            ('low', 'high'): 'medium',
            ('low', 'medium'): 'low',
            ('low', 'low'): 'low'
        }
        return severity_map.get((pattern_severity, criticality), 'medium')
    
    def generate_validation_code(self, rules: List[Dict[str, Any]], 
                                framework: str = 'pandas') -> str:
        """
        Generate validation code for a framework
        
        Args:
            rules: List of DQ rules
            framework: Target framework (pandas, great_expectations, deequ)
            
        Returns:
            Validation code as string
        """
        if framework == 'pandas':
            return self._generate_pandas_code(rules)
        elif framework == 'great_expectations':
            return self._generate_ge_code(rules)
        else:
            return "# Framework not supported yet"
    
    def _generate_pandas_code(self, rules: List[Dict[str, Any]]) -> str:
        """Generate pandas validation code"""
        code = "import pandas as pd\n\n"
        code += "def validate_data(df: pd.DataFrame) -> dict:\n"
        code += "    \"\"\"Validate DataFrame against DQ rules\"\"\"\n"
        code += "    results = {'passed': [], 'failed': []}\n\n"
        
        for i, rule in enumerate(rules):
            code += f"    # Rule {i+1}: {rule['description']}\n"
            code += f"    if {rule['validation_code']}:\n"
            code += f"        results['passed'].append('{rule['column']} - {rule['rule_type']}')\n"
            code += f"    else:\n"
            code += f"        results['failed'].append('{rule['failure_message']}')\n\n"
        
        code += "    return results\n"
        return code
    
    def _generate_ge_code(self, rules: List[Dict[str, Any]]) -> str:
        """Generate Great Expectations code"""
        code = "import great_expectations as ge\n\n"
        code += "# Great Expectations suite\n"
        code += "expectations = [\n"
        
        for rule in rules:
            if rule['rule_type'] == 'not_null':
                code += f"    ge.expect_column_values_to_not_be_null('{rule['column']}'),\n"
            elif rule['rule_type'] == 'range_validation':
                code += f"    ge.expect_column_values_to_be_between('{rule['column']}', "
                code += f"min_value={rule['min']}, max_value={rule['max']}),\n"
        
        code += "]\n"
        return code
