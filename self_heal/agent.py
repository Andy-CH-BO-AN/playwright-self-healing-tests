import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from self_heal import SelfHealError
from self_heal.evidence import FailureContext


class RepairCandidate(BaseModel):
    file: str
    old: str
    new: str
    reason: str
    confidence: int = Field(ge=1, le=100)


class RepairPlan(BaseModel):
    repairs: list[RepairCandidate]


def build_repair_prompt(contexts: list[FailureContext]) -> str:
    prompt_path = Path("ai/prompts/locator-repair.md")
    if not prompt_path.is_file():
        raise SelfHealError(f"Prompt file '{prompt_path}' does not exist")

    prompt_template = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt_template:
        raise SelfHealError(f"Prompt file '{prompt_path}' is empty")

    sections = [prompt_template, "\n## Actual Failure Context\n"]

    for i, ctx in enumerate(contexts, 1):
        po_sections = []
        for po_path, po_content in sorted(ctx.relevant_page_objects.items()):
            po_sections.append(
                f"""##### `{po_path}`
```python
{po_content}
```"""
            )
        page_object_context = "\n\n".join(po_sections) or "(none found)"

        section = f"""### Failure {i} (`{ctx.nodeid or "Unknown"}`)

#### 1. Failure Evidence (`failure.json`)
```json
{json.dumps(ctx.failure_data, indent=2, ensure_ascii=False)}
```

#### 2. DOM Snapshot (`page.html`)
```html
{ctx.dom_snapshot}
```

#### 3. Relevant Page Object Sources
{page_object_context}

#### 4. Failing Test Source (`{ctx.test_file or "Unknown"}`)
```python
{ctx.test_source}
```
"""
        sections.append(section)

    return "\n".join(sections)


def request_repair_plan(contexts: list[FailureContext]) -> RepairPlan:
    user_prompt = build_repair_prompt(contexts)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SelfHealError("GEMINI_API_KEY is not set in the environment or .env file")

    model_name = os.getenv("SELF_HEAL_MODEL", "gemini-3.5-flash-lite")

    print(f"Calling Gemini model '{model_name}' for failure diagnosis...")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RepairPlan,
                temperature=0.1,
            ),
        )
        if not response.text:
            raise SelfHealError("Received empty response from Gemini model")
        return RepairPlan.model_validate_json(response.text)
    except SelfHealError:
        raise
    except Exception as e:
        raise SelfHealError(f"LLM call failed: {e}") from e
