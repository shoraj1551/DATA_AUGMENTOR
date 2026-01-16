from llm.client import get_client
from utils.cache import llm_cache
from config.settings import get_model_for_feature, get_model_for_language
from utils.safe_llm_parser import SafeLLMParser
import difflib
import json


def calculate_code_similarity(code1: str, code2: str) -> float:
    """
    Calculate similarity between two code snippets.
    Returns a value between 0.0 (completely different) and 1.0 (identical).
    """
    # Remove whitespace and normalize for comparison
    normalized1 = ''.join(code1.split())
    normalized2 = ''.join(code2.split())
    
    # Use difflib to calculate similarity ratio
    similarity = difflib.SequenceMatcher(None, normalized1, normalized2).ratio()
    return similarity


# Helper for dynamic model selection
def get_best_model(language: str) -> str:
    """
    Select the best free model based on language complexity.
    - Python/SQL/R: Meta-Llama 3.1 8B (Great for standard tasks)
    - C++/Java/Rust/Go/JS: Qwen 2.5 7B (Better at complex syntax/logic)
    """
    complex_languages = ['cpp', 'c++', 'c', 'java', 'rust', 'go', 'typescript', 'javascript', 'js', 'ts', 'scala', 'kotlin', 'swift']
    
    # Check regular config first
    default_model = get_model_for_feature("code_review")
    
    # If language requires stronger reasoning/syntax capabilities, try to use Qwen if available as alternative
    if language.lower() in complex_languages:
        # Hardcoded check for free tier known models or check specific config
        # Ideally this comes from config, but for now we enforce logic as requested
        return "qwen/qwen-2.5-7b-instruct"
        
    return default_model


@llm_cache.cached
def review_code_with_llm(code: str, language: str, filename: str) -> str:
    """
    Use LLM to review code and return a detailed markdown report.
    """
    model = get_model_for_language(language)
    
    system_prompt = f"""You are an expert code reviewer for {language}.

Analyze the code for:
- Code quality issues
- Security vulnerabilities
- Performance problems
- Best practice violations
- Potential bugs

OUTPUT FORMAT:
Return a clear, well-structured MARKDOWN report.
- Use headers for categories (Security, Performance, etc.)
- Use bullet points for specific issues
- Cite specific line numbers if possible
- Be concise but professional
- Do NOT output JSON"""

    user_prompt = f"""Review this {language} code from '{filename}':

```{language}
{code[:5000]}  # Limit to first 5000 chars
```

Return a comprehensive markdown review report."""

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content


@llm_cache.cached
def generate_unit_tests_with_llm(code: str, language: str, test_framework: str) -> str:
    """
    Generate unit tests for the code.
    """
    model = get_model_for_language(language)
    
    system_prompt = f"""You are an expert test engineer for {language}.

Generate comprehensive UNIT tests using {test_framework}.

CRITICAL REQUIREMENTS:
1. ISOLATION: Mock ALL external dependencies (databases, APIs, file I/O, network calls)
2. Test individual functions/methods in complete isolation
3. Focus on testing the logic of ONE function at a time
4. Include edge cases, boundary conditions, and negative test cases

OUTPUT FORMAT:
Provide your response in TWO parts:

**Part 1: Natural Language Explanation**
Write 2-3 sentences explaining:
- What aspects of the code you're testing
- Why these unit tests are important
- What mocking strategy you used

**Part 2: Complete Test Code**
```{language}
[Your complete, runnable test code here]
```

Return both parts."""

    user_prompt = f"""Generate {test_framework} UNIT tests for this {language} code:

```{language}
{code[:5000]}
```

Remember: Unit tests = ISOLATED testing with MOCKED dependencies."""

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content


@llm_cache.cached
def generate_functional_tests_with_llm(code: str, language: str, test_framework: str) -> str:
    """
    Generate functional/integration tests.
    """
    model = get_model_for_language(language)
    
    system_prompt = f"""You are an expert test engineer for {language}.

FIRST: Analyze if this code has meaningful integration points or workflows.

If the code is a simple pure function with NO external dependencies, NO database calls, NO API calls, and NO multi-component workflows:
→ Return EXACTLY: "SAME AS UNIT TEST"

Otherwise, generate FUNCTIONAL/INTEGRATION tests using {test_framework}.

CRITICAL REQUIREMENTS for Functional Tests:
1. NO MOCKING: Test the REAL integration between components
2. Test complete WORKFLOWS (e.g., user input → processing → database → output)
3. Test how multiple functions/classes work TOGETHER
4. Test actual database queries, API calls, file operations (if present)
5. Test end-to-end scenarios with realistic data

OUTPUT FORMAT (if not "SAME AS UNIT TEST"):
Provide your response in TWO parts:

**Part 1: Natural Language Explanation**
Write 2-3 sentences explaining:
- What workflows or integration points you're testing
- How these differ from unit tests (what's NOT mocked)
- What end-to-end scenarios you're covering

**Part 2: Complete Test Code**
```{language}
[Your complete, runnable test code here]
```

Return both parts OR "SAME AS UNIT TEST"."""

    user_prompt = f"""Generate {test_framework} FUNCTIONAL tests for this {language} code:

```{language}
{code[:5000]}
```

Remember: Functional tests = REAL workflows, NO mocking, test INTEGRATION."""

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content


@llm_cache.cached
def generate_failure_scenarios_with_llm(code: str, language: str) -> str:
    """
    Generate failure scenarios and edge case inputs.
    """
    model = get_model_for_language(language)
    
    system_prompt = f"""You are a security and QA expert for {language}.

Generate ALL potential failure scenarios that could break this code. Be exhaustive.

Focus on:
- Edge case inputs (empty strings, null, undefined, zero, negative numbers)
- Boundary values (max int, min int, very large strings)
- Invalid types (string instead of number, null instead of object)
- Malformed data (invalid JSON, corrupted files, bad encoding)
- Security attack vectors (SQL injection, XSS, buffer overflow)
- Concurrency issues (race conditions, deadlocks)
- Resource exhaustion (memory leaks, infinite loops)

CRITICAL: Return ONLY valid JSON. Escape all special characters properly.
Use this EXACT structure:

{{
  "scenarios": [
    {{
      "function": "function_name",
      "input": "test input value",
      "reason": "why this causes failure",
      "expected": "expected exception or error"
    }}
  ]
}}

IMPORTANT: 
- Keep "input" and "reason" fields SHORT (under 100 characters)
- Properly escape quotes and newlines in JSON strings
- Do NOT include code blocks or markdown
- Return ONLY the raw JSON object"""

    user_prompt = f"""Generate failure scenarios for this {language} code:

```{language}
{code[:5000]}
```

Return ONLY valid JSON with the exact structure specified."""

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    # Use SafeLLMParser to parse JSON
    # This handles markdown stripping, regex finding, etc.
    failures = SafeLLMParser.parse_json(content, default={"scenarios": []})
    
    # Return as JSON string for consistency with cache and downstream usage
    return json.dumps(failures)


# ============================================
# NEW FEATURES
# ============================================

@llm_cache.cached
def add_comments_and_documentation(code: str, language: str) -> str:
    """
    Add inline comments and documentation to code WITHOUT changing code format or logic.
    Uses free LLM from config.
    """
    model = get_model_for_language(language)
    
    system_prompt = f"""You are an expert {language} developer and technical writer.

🚨🚨🚨 ABSOLUTE CRITICAL RULES - NEVER VIOLATE 🚨🚨🚨

1. KEEP THE EXACT SAME FORMAT
   - Input language MUST match Output language (e.g., Python → Python, Java → Java)
   - NEVER convert to JSON or any other format

2. ONLY ADD COMMENTS - NOTHING ELSE
   - Do NOT change function names
   - Do NOT change variable names
   - Do NOT change logic
   - Do NOT change imports
   - Do NOT change structure
   - ONLY add comment lines and docstrings using the correct syntax for {language}

3. EXAMPLES OF CORRECT OUTPUT:

Example 1 (Python):
INPUT:
def calculate(x, y):
    result = x + y
    return result

OUTPUT:
def calculate(x, y):
    \"\"\"Calculate sum of two numbers.\"\"\"
    # Add the two input values
    result = x + y
    return result

Example 2 (C++/Java/JavaScript):
INPUT:
int calculate(int x, int y) {{
    return x + y;
}}

OUTPUT:
/**
 * Calculate sum of two numbers.
 */
int calculate(int x, int y) {{
    // Add the two input values
    return x + y;
}}

WRONG OUTPUT (DO NOT DO THIS):
{{
  "function": "calculate",
  "parameters": ["x", "y"]
}}

4. WHAT TO ADD:
   - Docstrings for functions/classes (use correct {language} syntax)
   - Inline comments explaining WHY (not what)
   - Parameter descriptions
   - Return value descriptions

5. OUTPUT FORMAT:
   - Return the SAME programming language as input
   - Do NOT wrap in markdown code blocks
   - Do NOT convert to JSON
   - Just the code with comments added"""

    user_prompt = f"""Add ONLY comments to this {language} code. Keep it as {language} code!

INPUT CODE:
{code}

INSTRUCTIONS:
- Keep the EXACT SAME format ({language})
- ONLY add comment lines (use correct syntax for {language})
- Do NOT convert to JSON or any other format
- Return {language} code with comments added

OUTPUT (must be {language} code):"""

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    # Clean up response - remove markdown code blocks if present
    return SafeLLMParser.strip_markdown(response.choices[0].message.content)


@llm_cache.cached
def fix_all_issues(code: str, language: str, issues: object, failure_scenarios: list) -> dict:
    """
    Auto-fix all identified issues AND provide a structured log of changes.
    Returns JSON dict: { "fixed_code": str, "changes": list[dict] }
    """
    model = get_model_for_language(language)
    
    # Format issues and failures for the prompt
    if isinstance(issues, list):
        issues_text = "\n".join([
            f"- Line {issue.get('line', 'N/A')}: {issue.get('message', '')} (Severity: {issue.get('severity', 'unknown')})"
            for issue in issues
        ])
    else:
        # If issues is a string (markdown report), use it directly
        issues_text = str(issues)
    
    failures_text = "\n".join([
        f"- {scenario.get('function', 'General')}: {scenario.get('reason', '')} (Input: {scenario.get('input', 'N/A')})"
        for scenario in failure_scenarios
    ])
    
    system_prompt = f"""You are an expert {language} developer.

Fix ALL identified issues and add error handling for ALL failure scenarios.

REQUIREMENTS:
1. Fix every issue mentioned in the code review
2. Add proper error handling for all failure scenarios
3. Add input validation
4. Add try-catch blocks where appropriate
5. Maintain original functionality
6. Follow {language} best practices

RESPONSE FORMAT:
Return a VALID JSON object with TWO fields:
1. "fixed_code": The complete, compilable fixed code string.
2. "changes": A list of objects explaining what changed.

JSON STRUCTURE:
{{
  "fixed_code": "...",
  "changes": [
    {{
      "issue_summary": "Short summary of the issue fixed",
      "fix_explanation": "Detailed explanation of what code was changed",
      "line_number": <approx_line_number_in_new_code>
    }}
  ]
}}

CRITICAL:
- Return ONLY valid JSON
- Escape newlines and quotes in the "fixed_code" string properly
- The "fixed_code" must be the WHOLE file, not just snippets"""

    user_prompt = f"""Fix this {language} code by addressing ALL issues and failure scenarios:

**ORIGINAL CODE:**
```{language}
{code}
```

**ISSUES TO FIX:**
{issues_text if issues_text else "No issues identified"}

**FAILURE SCENARIOS TO HANDLE:**
{failures_text if failures_text else "No failure scenarios identified"}

Return the structured JSON with fixed code and change log."""

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    # Use SafeLLMParser to parse JSON response
    return SafeLLMParser.parse_json(content, default={
        "fixed_code": content if not content.strip().startswith('{') else "",
        "changes": [{"issue_summary": "Parsing Error", "fix_explanation": "LLM returned raw text. Code may be fixed but details are missing.", "line_number": 0}]
    })
