"""
06_spec_generate.py
===================
Generate automated requirements from automated personas.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

from groq import Groq

GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
REQS_PER_PERSONA = 2

PERSONAS_PATH = Path("personas/personas_auto.json")
GROUPS_PATH = Path("data/review_groups_auto.json")
SPEC_PATH = Path("spec/spec_auto.md")

SPEC_PROMPT = """\
You are a software requirements engineer for the Headspace Android meditation app.

Below is a user persona derived from real user reviews:

Persona ID   : {persona_id}
Persona Name : {persona_name}
Description  : {description}
Goals        : {goals}
Pain Points  : {pain_points}
Constraints  : {constraints}
Review Group : {group_id} - {group_theme}

Task:
Generate exactly {n} distinct functional requirements this persona motivates.
Each requirement must address a different aspect of the persona's goals or pain points.
Use concrete, measurable language. Avoid vague words such as fast, easy, good, user-friendly, better, seamless, or appropriate.

Respond only with a valid JSON array:

[
  {{
    "req_id": "{req_id_prefix}1",
    "description": "The system shall <specific, measurable behaviour>.",
    "acceptance_criteria": [
      "Given <precondition>,",
      "When <action>,",
      "Then <verifiable outcome with measurable threshold>."
    ]
  }},
  {{
    "req_id": "{req_id_prefix}2",
    "description": "The system shall <specific, measurable behaviour>.",
    "acceptance_criteria": [
      "Given <precondition>,",
      "When <action>,",
      "Then <verifiable outcome with measurable threshold>."
    ]
  }}
]
"""


def groq_call(client: Groq, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=900,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            wait = 2 ** attempt
            print(f"  [groq] attempt {attempt + 1} failed: {exc}. Retry in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Groq API failed after retries.")


def parse_json_array(raw: str) -> list[dict]:
    clean = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(clean)


def render_requirement(req: dict, persona_id: str, persona_name: str, group_id: str, group_theme: str) -> str:
    ac_block = "\n".join(f"  - {line}" for line in req.get("acceptance_criteria", []))
    return (
        f"# Requirement ID: {req['req_id']}\n\n"
        f"- **Description:** {req['description']}\n"
        f"- **Source Persona:** {persona_id} - {persona_name}\n"
        f"- **Traceability:** Derived from review group {group_id} ({group_theme})\n"
        f"- **Acceptance Criteria:**\n"
        f"{ac_block}\n"
    )


def run() -> None:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        sys.exit("Error: set GROQ_API_KEY before running.")

    client = Groq(api_key=api_key)
    print(f"[init]  model: {GROQ_MODEL}")

    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)

    personas = json.loads(PERSONAS_PATH.read_text(encoding="utf-8"))["personas"]
    print(f"[load]  {len(personas)} personas from {PERSONAS_PATH}")

    group_themes = {}
    if GROUPS_PATH.exists():
        for group in json.loads(GROUPS_PATH.read_text(encoding="utf-8"))["groups"]:
            group_themes[group["group_id"]] = group["theme"]

    header = (
        "# Headspace Android App - Automated Functional Requirements Specification\n"
        "**Project:** Headspace Android (com.getsomeheadspace.android)\n"
        "**Pipeline Stage:** Automated (Task 4.3)\n"
        f"**Source:** {PERSONAS_PATH}  ({len(personas)} personas)\n"
        f"**Groups:** {GROUPS_PATH}\n\n"
        "---\n"
    )
    sections = [header]
    req_counter = 1

    for persona in personas:
        persona_id = persona["id"]
        persona_name = persona["name"]
        group_id = persona["derived_from_group"]
        group_theme = group_themes.get(group_id, group_id)
        persona_num = persona_id.split("_")[-1]
        req_id_prefix = f"FR_auto_{persona_num}_"

        print(f"\n[persona {persona_id}] {persona_name}  (group {group_id})")
        prompt = SPEC_PROMPT.format(
            persona_id=persona_id,
            persona_name=persona_name,
            description=persona.get("description", ""),
            goals="; ".join(persona.get("goals", [])),
            pain_points="; ".join(persona.get("pain_points", [])),
            constraints="; ".join(persona.get("constraints", [])),
            group_id=group_id,
            group_theme=group_theme,
            n=REQS_PER_PERSONA,
            req_id_prefix=req_id_prefix,
        )

        print(f"  [groq] generating {REQS_PER_PERSONA} requirements...")
        requirements = parse_json_array(groq_call(client, prompt))
        for requirement in requirements:
            requirement["req_id"] = f"FR_auto_{req_counter}"
            req_counter += 1
            sections.append(render_requirement(requirement, persona_id, persona_name, group_id, group_theme) + "\n---\n")
            print(f"  -> {requirement['req_id']}: {requirement['description'][:80]}...")

    SPEC_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"\n[save]  spec -> {SPEC_PATH}")
    print(f"Done - {req_counter - 1} requirements written.")


if __name__ == "__main__":
    run()
