from llm.client import get_client
from utils.cache import llm_cache
from config.settings import get_model_for_feature
import difflib


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



@llm_cache.cached
def review_code_with_llm(code: str, language: str, filename: str) -> dict:
    """
    Use LLM to review code for issues, best practices, and security concerns.
    """
    system_prompt = f"""You are an expert code reviewer for {language}.

Analyze the code for:
- Code quality issues
- Security vulnerabilities
- Performance problems
- Best practice violations
- Potential bugs

Return JSON with this structure:
{{
  "issues": [
    {{
      "line": <line_number>,
      "severity": "high|medium|low",
      "type": "security|performance|quality|bug",
      "message": "Description of the issue",
      "suggestion": "How to fix it"
    }}
  ]
}}"""

    user_prompt = f"""Review this {language} code from '{filename}':

```{language}
{code[:5000]}  # Limit to first 5000 chars
```

Return ONLY valid JSON with code review findings."""

    response = get_client().chat.completions.create(
        model=get_model_for_feature("code_review"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


@llm_cache.cached
def generate_unit_tests_with_llm(code: str, language: str, test_framework: str) -> str:
    """
    Generate unit tests for the code.
    """
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
        model=get_model_for_feature("code_review"),
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
        model=get_model_for_feature("code_review"),
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
        model=get_model_for_feature("code_review"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


# ============================================
# NEW FEATURES
# ============================================

@llm_cache.cached
def add_comments_and_documentation(code: str, language: str) -> str:
    """
    Add inline comments and documentation to code WITHOUT changing code format or logic.
    Uses free LLM from config.
    """
    system_prompt = f"""You are an expert {language} developer and technical writer.

🚨🚨🚨 ABSOLUTE CRITICAL RULES - NEVER VIOLATE 🚨🚨🚨

1. KEEP THE EXACT SAME FORMAT
   - If input is Python → output MUST be Python
   - If input is SQL → output MUST be SQL
   - If input is JavaScript → output MUST be JavaScript
   - NEVER convert to JSON or any other format

2. ONLY ADD COMMENTS - NOTHING ELSE
   - Do NOT change function names
   - Do NOT change variable names
   - Do NOT change logic
   - Do NOT change imports
   - Do NOT change structure
   - ONLY add comment lines and docstrings

3. EXAMPLE OF CORRECT OUTPUT:

INPUT (Python):
def calculate(x, y):
    result = x + y
    # CRITICAL: Check if LLM returned JSON instead of code
    result_stripped = result.strip()
    if result_stripped.startswith('{') or result_stripped.startswith('['):
        raise ValueError(
            "? LLM returned JSON instead of code.\n\n"
            "Free LLM models are not following instructions.\n"
            "Please use the SKIP button to bypass documentation."
        )
    
    return result

CORRECT OUTPUT (Python with comments):
def calculate(x, y):
    \"\"\"Calculate sum of two numbers.\"\"\"
    # Add the two input values
    result = x + y
    # CRITICAL: Check if LLM returned JSON instead of code
    result_stripped = result.strip()
    if result_stripped.startswith('{') or result_stripped.startswith('['):
        raise ValueError(
            "? LLM returned JSON instead of code.\n\n"
            "Free LLM models are not following instructions.\n"
            "Please use the SKIP button to bypass documentation."
        )
    
    return result

WRONG OUTPUT (DO NOT DO THIS):
{{
  "function": "calculate",
  "parameters": ["x", "y"]
}}

4. WHAT TO ADD:
   - Docstrings for functions/classes
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
- ONLY add comment lines
- Do NOT convert to JSON or any other format
- Return {language} code with comments added

OUTPUT (must be {language} code):"""

    response = get_client().chat.completions.create(
        model=get_model_for_feature("code_review"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    # Clean up response - remove markdown code blocks if present
    result = response.choices[0].message.content
    
    # Remove markdown code blocks
    if result.startswith("```"):
        lines = result.split('\n')
        # Remove first line (```language) and last line (```)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        result = '\n'.join(lines)
    
    # CRITICAL: Check if LLM returned JSON instead of code
    result_stripped = result.strip()
    if result_stripped.startswith('{') or result_stripped.startswith('['):
        raise ValueError(
            "? LLM returned JSON instead of code.\n\n"
            "Free LLM models are not following instructions.\n"
            "Please use the SKIP button to bypass documentation."
        )
    
    return result


@llm_cache.cached
def fix_all_issues(code: str, language: str, issues: list, failure_scenarios: list) -> str:
    """
    Auto-fix all identified issues and handle failure scenarios.
    Uses free LLM from config.
    """
    # Format issues and failures for the prompt
    issues_text = "\n".join([
        f"- Line {issue.get('line', 'N/A')}: {issue.get('message', '')} (Severity: {issue.get('severity', 'unknown')})"
        for issue in issues
    ])
    
    failures_text = "\n".join([
        f"- {scenario.get('function', 'General')}: {scenario.get('reason', '')} (Input: {scenario.get('input', 'N/A')})"
        for scenario in failure_scenarios
    ])
    
    system_prompt = f"""You are an expert {language} developer.

Fix ALL identified issues and add error handling for ALL failure scenarios.

REQUIREMENTS:
1. Fix every issue mentioned in the code review
2. Add proper error handling for all failure scenarios
3. Add input validation to prevent failures
4. Add try-catch blocks where appropriate
5. Add defensive programming checks (null checks, type checks, boundary checks)
6. Maintain the original functionality
7. Follow {language} best practices

CRITICAL:
- Fix ALL issues, don't skip any
- Handle ALL failure scenarios
- Add comprehensive error handling
- Keep the code readable and maintainable

OUTPUT FORMAT:
Return ONLY the complete fixed code.
Do NOT include explanations or markdown - just the code."""

    user_prompt = f"""Fix this {language} code by addressing ALL issues and failure scenarios:

**ORIGINAL CODE:**
```{language}
{code}
```

**ISSUES TO FIX:**
{issues_text if issues_text else "No issues identified"}

**FAILURE SCENARIOS TO HANDLE:**
{failures_text if failures_text else "No failure scenarios identified"}

Return the complete fixed code with all issues resolved and all failure scenarios handled."""

    response = get_client().chat.completions.create(
        model=get_model_for_feature("code_review"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content

