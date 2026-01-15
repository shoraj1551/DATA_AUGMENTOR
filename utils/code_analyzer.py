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
    """Extract code from Jupyter notebook."""
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
        
        if 'cells' not in notebook:
            raise ValueError("Notebook is missing 'cells' field. This may not be a valid Jupyter notebook.")
        
        code_cells = []
        
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                if isinstance(source, list):
                    code_cells.append(''.join(source))
                else:
                    code_cells.append(source)
        
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
