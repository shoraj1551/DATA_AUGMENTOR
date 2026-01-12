from llm.client import get_client
from utils.cache import llm_cache
from config.settings import get_model_for_feature


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
