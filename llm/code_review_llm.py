from llm.client import get_client
from utils.cache import llm_cache
from config.settings import MODEL_NAME


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
        model="openai/gpt-4o-mini",
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

Generate comprehensive unit tests using {test_framework}.

Requirements:
- Test all functions
- Include edge cases
- Test boundary conditions
- Add negative test cases
- Use proper assertions

Return ONLY the test code, no explanations."""

    user_prompt = f"""Generate {test_framework} unit tests for this {language} code:

```{language}
{code[:5000]}
```

Return complete, runnable test code."""

    response = get_client().chat.completions.create(
        model="openai/gpt-4o-mini",
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

Generate functional/integration tests using {test_framework}.

Focus on:
- Component interactions
- End-to-end workflows
- Integration scenarios
- API testing (if applicable)

Return ONLY the test code."""

    user_prompt = f"""Generate {test_framework} functional tests for this {language} code:

```{language}
{code[:5000]}
```

Return complete, runnable test code."""

    response = get_client().chat.completions.create(
        model="openai/gpt-4o-mini",
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

Generate failure scenarios that could break this code:
- Edge case inputs
- Boundary values
- Invalid types
- Malformed data
- Security attack vectors

Return JSON:
{{
  "scenarios": [
    {{
      "function": "function_name",
      "input": "test input",
      "reason": "why this might fail",
      "expected": "expected behavior"
    }}
  ]
}}"""

    user_prompt = f"""Generate failure scenarios for this {language} code:

```{language}
{code[:5000]}
```

Return ONLY valid JSON."""

    response = get_client().chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content
