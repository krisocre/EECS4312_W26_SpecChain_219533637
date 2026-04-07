"""
07_tests_generate.py
====================
Generate automated tests from automated requirements.
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
TESTS_PER_REQ = 2

SPEC_PATH = Path("spec/spec_auto.md")
TESTS_PATH = Path("tests/tests_auto.json")

TEST_PROMPT = """\
You are a QA engineer writing validation tests for the Headspace Android app.

Requirement ID : {req_id}
Description    : {description}
Acceptance Criteria:
{ac}

Write exactly {n} distinct test scenarios that together verify this requirement.
Cover different angles: one happy-path scenario and one edge or boundary scenario.

Respond only with a valid JSON array:

[
  {{
    "scenario": "<10-15 word scenario title>",
    "steps": [
      "<step 1 - specific, executable action>",
      "<step 2>",
      "<step 3>",
      "<step 4>"
    ],
    "expected_result": "<single sentence: verifiable outcome that maps to the acceptance criteria>"
  }},
  {{
    "scenario": "<10-15 word scenario title>",
    "steps": [
      "<step 1>",
      "<step 2>",
      "<step 3>",
      "<step 4>"
    ],
    "expected_result": "<single sentence: verifiable outcome>"
  }}
]
"""


def parse_spec(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"(?=# Requirement ID: FR_auto_)", text)
    requirements = []
    for block in blocks:
        id_match = re.search(r"# Requirement ID: (FR_auto_\d+)", block)
        if not id_match:
            continue
        desc_match = re.search(r"\*\*Description:\*\*\s*(.+?)(?=\n- \*\*|\Z)", block, re.DOTALL)
        ac_match = re.search(r"\*\*Acceptance Criteria:\*\*\s*(.*?)(?=\n---|\Z)", block, re.DOTALL)
        requirements.append({
            "req_id": id_match.group(1),
            "description": desc_match.group(1).strip() if desc_match else "",
            "ac": ac_match.group(1).strip() if ac_match else "",
        })
    return requirements


def groq_call(client: Groq, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=900,
                temperature=0.25,
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


def run() -> None:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        sys.exit("Error: set GROQ_API_KEY before running.")

    client = Groq(api_key=api_key)
    print(f"[init]  model: {GROQ_MODEL}")

    TESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    requirements = parse_spec(SPEC_PATH)
    print(f"[parse] {len(requirements)} requirements from {SPEC_PATH}")

    tests_out = {"tests": []}
    test_counter = 1

    for requirement in requirements:
        req_id = requirement["req_id"]
        print(f"\n[req]   {req_id}: {requirement['description'][:70]}...")
        prompt = TEST_PROMPT.format(
            req_id=req_id,
            description=requirement["description"],
            ac=requirement["ac"],
            n=TESTS_PER_REQ,
        )

        print(f"  [groq] generating {TESTS_PER_REQ} test scenarios...")
        tests = parse_json_array(groq_call(client, prompt))
        for test in tests:
            tests_out["tests"].append({
                "test_id": f"T_auto_{test_counter}",
                "requirement_id": req_id,
                "scenario": test.get("scenario", ""),
                "steps": test.get("steps", []),
                "expected_result": test.get("expected_result", ""),
            })
            print(f"  -> T_auto_{test_counter}: {test.get('scenario', '')[:60]}")
            test_counter += 1

    TESTS_PATH.write_text(json.dumps(tests_out, indent=2), encoding="utf-8")
    print(f"\n[save]  {len(tests_out['tests'])} tests -> {TESTS_PATH}")
    print("Done.")


if __name__ == "__main__":
    run()
