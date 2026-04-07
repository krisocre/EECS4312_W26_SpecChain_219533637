"""Run the automated pipeline from start to finish."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# These are the programmatic steps only.
# Manual and hybrid work still need to be reviewed separately.
STEPS = [
    ("Validate repository", "src/00_validate_repo.py"),
    ("Clean raw reviews", "src/02_clean.py"),
    ("Generate automated personas", "src/05_personas_auto.py"),
    ("Generate automated specification", "src/06_spec_generate.py"),
    ("Generate automated tests", "src/07_tests_generate.py"),
    ("Compute automated metrics", "src/08_metrics.py"),
]


def run_step(label: str, script_path: str) -> None:
    print(f"\n=== {label} ===")
    subprocess.run([sys.executable, script_path], cwd=ROOT, check=True)


def main() -> int:
    if not os.environ.get("GROQ_API_KEY"):
        print("Set GROQ_API_KEY before running this script.")
        return 1

    # Order:
    # 1. check files
    # 2. clean data -> data/reviews_clean.jsonl
    # 3. build auto groups/personas -> data/review_groups_auto.json, personas/personas_auto.json
    # 4. build auto spec -> spec/spec_auto.md
    # 5. build auto tests -> tests/tests_auto.json
    # 6. compute auto metrics -> metrics/metrics_auto.json
    for label, script_path in STEPS:
        run_step(label, script_path)

    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
