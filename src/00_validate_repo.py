"""Small script to check that the repo has the required files and folders."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_DIRS = [
    "data",
    "metrics",
    "personas",
    "prompts",
    "reflection",
    "spec",
    "src",
    "tests",
]

REQUIRED_FILES = [
    "README.md",
    "data/reviews_raw.jsonl",
    "data/reviews_clean.jsonl",
    "data/dataset_metadata.json",
    "data/review_groups_manual.json",
    "data/review_groups_auto.json",
    "data/review_groups_hybrid.json",
    "personas/personas_manual.json",
    "personas/personas_auto.json",
    "personas/personas_hybrid.json",
    "spec/spec_manual.md",
    "spec/spec_auto.md",
    "spec/spec_hybrid.md",
    "tests/tests_manual.json",
    "tests/tests_auto.json",
    "tests/tests_hybrid.json",
    "metrics/metrics_manual.json",
    "metrics/metrics_auto.json",
    "metrics/metrics_hybrid.json",
    "metrics/metrics_summary.json",
    "reflection/reflection.md",
    "src/01_collect_or_import.py",
    "src/02_clean.py",
    "src/03_manual_coding_template.py",
    "src/04_personas_manual.py",
    "src/05_personas_auto.py",
    "src/06_spec_generate.py",
    "src/07_tests_generate.py",
    "src/08_metrics.py",
    "src/run_all.py",
]


def count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def main() -> int:
    root = Path.cwd()
    missing: list[str] = []
    print("Checking repository structure...")

    for directory in REQUIRED_DIRS:
        path = root / directory
        if not path.is_dir():
            missing.append(directory)
        else:
            print(f"{directory}/ found")

    for file_path in REQUIRED_FILES:
        path = root / file_path
        if not path.exists():
            missing.append(file_path)
        else:
            print(f"{file_path} found")

    if missing:
        print("[validate] Missing required repo items:")
        for item in missing:
            print(f"  - {item}")
        return 1

    raw_path = root / "data/reviews_raw.jsonl"
    clean_path = root / "data/reviews_clean.jsonl"
    metadata_path = root / "data/dataset_metadata.json"

    raw_count = count_jsonl_rows(raw_path)
    print(f"[validate] Raw dataset rows: {raw_count}")

    if clean_path.exists():
        clean_count = count_jsonl_rows(clean_path)
        print(f"[validate] Clean dataset rows: {clean_count}")
    else:
        print("[validate] Clean dataset not found yet: data/reviews_clean.jsonl")

    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            app_name = metadata.get("app_name") or metadata.get("app") or "unknown"
            print(f"[validate] Dataset metadata found for app: {app_name}")
        except json.JSONDecodeError:
            print("[validate] Warning: dataset_metadata.json exists but is not valid JSON.")
    else:
        print("[validate] Warning: data/dataset_metadata.json is missing.")

    print("Repository validation complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
