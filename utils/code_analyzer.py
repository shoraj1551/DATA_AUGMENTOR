import json
from typing import Dict, List, Any


def detect_language(filename: str) -> str:
    """Detect programming language from file extension."""
    ext = filename.lower().split('.')[-1]
    
    language_map = {
        # Python ecosystem
        'py': 'python',
        'ipynb': 'python',
        'pyw': 'python',
        
        # JavaScript/TypeScript
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'mjs': 'javascript',
        
        # JVM languages
        'java': 'java',
        'scala': 'scala',
        'kt': 'kotlin',
        'kts': 'kotlin',
        
        # .NET languages
        'cs': 'csharp',
        'vb': 'vb',
        'fs': 'fsharp',
        
        # Other compiled languages
        'go': 'go',
        'rs': 'rust',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'c': 'c',
        'h': 'c',
        'hpp': 'cpp',
        
        # Scripting languages
        'rb': 'ruby',
        'php': 'php',
        'pl': 'perl',
        'lua': 'lua',
        'sh': 'bash',
        'bash': 'bash',
        
        # Data & Query languages
        'sql': 'sql',
        'hql': 'hive',
        'r': 'r',
        
        # Web languages
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        
        # Other
        'swift': 'swift',
        'dart': 'dart',
        'groovy': 'groovy'
    }
    
    return language_map.get(ext, 'unknown')


def parse_notebook(ipynb_content: str) -> str:
    """Extract code from Jupyter notebook (supports v3, v4, v5 formats)."""
    try:
        # Validate content is not empty
        if not ipynb_content or not ipynb_content.strip():
            raise ValueError("Notebook content is empty")
        
        # Parse JSON
        try:
            notebook = json.loads(ipynb_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in notebook file. Error at position {e.pos}: {e.msg}")
        
        # Validate notebook structure
        if not isinstance(notebook, dict):
            raise ValueError("Notebook must be a JSON object")
        
        # Check notebook format version
        nbformat_version = notebook.get('nbformat', 0)
        
        # Handle different notebook formats
        code_cells = []
        
        # v4+ format (current standard)
        if 'cells' in notebook:
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') == 'code':
                    source = cell.get('source', [])
                    if isinstance(source, list):
                        code_cells.append(''.join(source))
                    else:
                        code_cells.append(source)
        
        # v3 format (older)
        elif 'worksheets' in notebook:
            for worksheet in notebook.get('worksheets', []):
                for cell in worksheet.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        source = cell.get('input', [])  # v3 uses 'input' instead of 'source'
                        if isinstance(source, list):
                            code_cells.append(''.join(source))
                        else:
                            code_cells.append(source)
        
        else:
            # Unknown format - provide diagnostic info
            available_keys = list(notebook.keys())
            raise ValueError(
                f"Unrecognized Jupyter notebook format.\n"
                f"Notebook version: {nbformat_version}\n"
                f"Available fields: {', '.join(available_keys)}\n"
                f"Expected 'cells' (v4+) or 'worksheets' (v3) field."
            )
        
        if not code_cells:
            raise ValueError("No code cells found in notebook. The notebook may be empty or contain only markdown cells.")
        
        return '\n\n'.join(code_cells)
    except ValueError as ve:
        # Re-raise ValueError with clear message
        raise ve
    except Exception as e:
        raise ValueError(f"Unexpected error parsing Jupyter notebook: {str(e)}")


def extract_functions(code: str, language: str) -> List[str]:
    """
    Extract function names from code (simple regex-based extraction).
    For production, use proper AST parsing.
    """
    import re
    
    patterns = {
        'python': r'def\s+(\w+)\s*\(',
        'javascript': r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(',
        'typescript': r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(',
        'java': r'(public|private|protected)?\s+\w+\s+(\w+)\s*\(',
        'csharp': r'(public|private|protected)?\s+\w+\s+(\w+)\s*\(',
        'go': r'func\s+(\w+)\s*\(',
        'ruby': r'def\s+(\w+)',
        'php': r'function\s+(\w+)\s*\('
    }
    
    pattern = patterns.get(language, r'function\s+(\w+)\s*\(')
    matches = re.findall(pattern, code)
    
    # Flatten tuples from regex groups
    functions = []
    for match in matches:
        if isinstance(match, tuple):
            functions.extend([m for m in match if m])
        else:
            functions.append(match)
    
    return list(set(functions))  # Remove duplicates


def get_test_framework(language: str) -> str:
    """Get appropriate test framework for language."""
    frameworks = {
        'python': 'pytest',
        'javascript': 'Jest',
        'typescript': 'Jest',
        'java': 'JUnit',
        'scala': 'ScalaTest',
        'kotlin': 'JUnit',
        'csharp': 'NUnit',
        'vb': 'NUnit',
        'fsharp': 'NUnit',
        'go': 'testing',
        'rust': 'cargo test',
        'cpp': 'Google Test',
        'c': 'Unity',
        'ruby': 'RSpec',
        'php': 'PHPUnit',
        'perl': 'Test::More',
        'lua': 'busted',
        'bash': 'bats',
        'sql': 'tSQLt',
        'hive': 'HiveQL',
        'r': 'testthat',
        'swift': 'XCTest',
        'dart': 'test',
        'groovy': 'Spock'
    }
    return frameworks.get(language, 'unittest')


def analyze_code_structure(code: str, language: str) -> Dict[str, Any]:
    """Analyze code structure and return metadata."""
    lines = code.split('\n')
    functions = extract_functions(code, language)
    
    return {
        'language': language,
        'lines_of_code': len(lines),
        'functions': functions,
        'function_count': len(functions),
        'test_framework': get_test_framework(language)
    }


def validate_code_syntax(code: str, language: str) -> bool:
    """
    Validate syntax of the code for supported languages.
    Returns True if syntax is valid or if language is not supported for validation.
    Returns False if syntax error is found.
    """
    if language == 'python':
        import ast
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
            
    elif language in ['javascript', 'typescript', 'java', 'cpp', 'c', 'csharp', 'go', 'rust', 'php', 'scala', 'kotlin', 'swift']:
        # For compiled/other languages where we don't have a runtime parser,
        # we perform heuristic validation for common structural errors.
        
        # 1. Check for matching braces/parentheses/brackets
        # This is the most common error in LLM-generated code
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        
        # Ignore brackets in strings/comments is hard with regex alone, so this is a "Simple" check.
        # It's better than nothing but can produce false positives if code has unbalanced braces in strings.
        # We'll use a slightly safer simple stack approach that ignores nothing for now (safe bet for code review)
        # or we accept that a string like " { " might break it. 
        # Let's try to be basic: strictly unmatched structural braces are usually bad.
        
        for char in code:
            if char in '({[':
                stack.append(char)
            elif char in ')}]':
                if not stack or stack[-1] != pairs[char]:
                    return False # Error: Unmatched closing brace or wrong type
                stack.pop()
        
        if stack:
            return False # Error: Unclosed opening brace
            
        return True

    # For JSON
    elif language == 'json':
        try:
            json.loads(code)
            return True
        except json.JSONDecodeError:
            return False
            
    # Default for others
    return True

