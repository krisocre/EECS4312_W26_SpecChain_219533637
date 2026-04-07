"""
08_metrics.py
=============
Compute pipeline metrics for the manual, automated, or hybrid artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CONFIGS = {
    "automated": {
        "dataset": Path("data/reviews_clean.jsonl"),
        "groups": Path("data/review_groups_auto.json"),
        "personas": Path("personas/personas_auto.json"),
        "spec": Path("spec/spec_auto.md"),
        "tests": Path("tests/tests_auto.json"),
        "output": Path("metrics/metrics_auto.json"),
    },
    "manual": {
        "dataset": Path("data/reviews_clean.jsonl"),
        "groups": Path("data/review_groups_manual.json"),
        "personas": Path("personas/personas_manual.json"),
        "spec": Path("spec/spec_manual.md"),
        "tests": Path("tests/tests_manual.json"),
        "output": Path("metrics/metrics_manual.json"),
    },
    "hybrid": {
        "dataset": Path("data/reviews_clean.jsonl"),
        "groups": Path("data/review_groups_hybrid.json"),
        "personas": Path("personas/personas_hybrid.json"),
        "spec": Path("spec/spec_hybrid.md"),
        "tests": Path("tests/tests_hybrid.json"),
        "output": Path("metrics/metrics_hybrid.json"),
    },
}

VAGUE_TERMS = [
    r"\bfast\b", r"\bquickly\b", r"\beasy\b", r"\beasily\b", r"\bbetter\b",
    r"\buser.friendly\b", r"\befficiently\b", r"\bseamless(ly)?\b", r"\bsimple\b",
    r"\bsimply\b", r"\bappropriate(ly)?\b", r"\badequate(ly)?\b", r"\breasonable\b",
    r"\btimely\b", r"\bsufficient(ly)?\b", r"\bproper(ly)?\b", r"\bgood\b",
    r"\bnice\b", r"\bimproved\b", r"\boptimal\b", r"\bintuitive(ly)?\b",
    r"\bconvenient(ly)?\b", r"\bsmooth(ly)?\b", r"\bmeaningfully\b",
]

THEME_KEYWORDS = {
    "crashes": ["crash", "freeze", "lag", "slow", "glitch", "unusable", "unresponsive", "buggy", "broken", "loading"],
    "navigation": ["navigate", "navigation", "find", "hard to find", "confusing", "search", "interface", "ui ", "design"],
    "subscription": ["paywall", "subscri", "price", "cost", "charged", "billing", "overpriced", "expensive", "free trial", "locked behind"],
    "positive": ["meditat", "relax", "calm", "sleep", "anxiety", "stress", "mindful", "peaceful", "helpful", "love"],
    "features": ["offline", "download", "screen off", "filter", "search", "playlist", "favourites", "feature"],
    "login": ["log in", "login", "sign in", "account", "locked out", "loop", "authenticate"],
}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_spec_requirements(spec_text: str) -> list[dict]:
    blocks = re.split(r"(?=# Requirement ID:)", spec_text)
    requirements = []
    for block in blocks:
        id_match = re.search(r"# Requirement ID:\s*(\S+)", block)
        if not id_match:
            continue
        desc_match = re.search(r"\*?\*?Description\*?\*?:?\*?\*?\s*\[?(.+?)\]?\n", block, re.DOTALL)
        ac_match = re.search(r"\*?\*?Acceptance Criteria\*?\*?:?\*?\*?\s*(.*?)(?:\n---|\Z)", block, re.DOTALL)
        requirements.append({
            "req_id": id_match.group(1).rstrip("."),
            "description": desc_match.group(1).strip() if desc_match else "",
            "ac": ac_match.group(1).strip() if ac_match else "",
            "full_block": block,
        })
    return requirements


def has_source_persona(block: str) -> bool:
    return bool(re.search(r"Source Persona", block, re.IGNORECASE))


def has_traceability(block: str) -> bool:
    return bool(re.search(r"Traceability", block, re.IGNORECASE))


def is_ambiguous(requirement: dict) -> bool:
    text = f"{requirement['description']} {requirement['ac']}"
    return any(re.search(term, text, re.IGNORECASE) for term in VAGUE_TERMS)


def review_coverage(reviews: list[dict]) -> float:
    covered = set()
    all_keywords = list(THEME_KEYWORDS.values())
    for review in reviews:
        content = review.get("content", "").lower()
        for keywords in all_keywords:
            if any(keyword in content for keyword in keywords):
                covered.add(review["reviewId"])
                break
    return round(len(covered) / len(reviews), 4) if reviews else 0.0


def compute(pipeline: str = "automated") -> dict:
    cfg = CONFIGS[pipeline]
    print(f"[metrics] pipeline: {pipeline}")

    reviews = load_jsonl(cfg["dataset"])
    personas = json.loads(cfg["personas"].read_text(encoding="utf-8")).get("personas", [])
    groups = json.loads(cfg["groups"].read_text(encoding="utf-8")).get("groups", [])
    requirements = parse_spec_requirements(cfg["spec"].read_text(encoding="utf-8"))
    tests = json.loads(cfg["tests"].read_text(encoding="utf-8")).get("tests", [])

    dataset_size = len(reviews)
    persona_count = len(personas)
    requirements_count = len(requirements)
    tests_count = len(tests)

    print(f"  dataset_size:       {dataset_size}")
    print(f"  persona_count:      {persona_count}")
    print(f"  requirements_count: {requirements_count}")
    print(f"  tests_count:        {tests_count}")

    review_to_group = sum(len(group.get("review_ids", [])) for group in groups)
    group_to_persona = persona_count
    persona_to_req = sum(1 for requirement in requirements if has_source_persona(requirement["full_block"]))
    req_to_test = len(tests)
    traceability_links = review_to_group + group_to_persona + persona_to_req + req_to_test

    print(
        f"  traceability_links: {traceability_links}  "
        f"(r->g:{review_to_group} g->p:{group_to_persona} p->r:{persona_to_req} r->t:{req_to_test})"
    )

    coverage = review_coverage(reviews)
    traceable = sum(
        1 for requirement in requirements
        if has_source_persona(requirement["full_block"]) and has_traceability(requirement["full_block"])
    )
    tested = sum(1 for requirement in requirements if requirement["req_id"] in {test["requirement_id"] for test in tests})
    ambiguous = sum(1 for requirement in requirements if is_ambiguous(requirement))

    traceability_ratio = round(traceable / requirements_count, 4) if requirements_count else 0
    testability_rate = round(tested / requirements_count, 4) if requirements_count else 0
    ambiguity_ratio = round(ambiguous / requirements_count, 4) if requirements_count else 0

    print(f"  review_coverage:    {coverage}")
    print(f"  traceability_ratio: {traceability_ratio}  ({traceable}/{requirements_count})")
    print(f"  testability_rate:   {testability_rate}  ({tested}/{requirements_count})")
    print(f"  ambiguity_ratio:    {ambiguity_ratio}  ({ambiguous}/{requirements_count})")

    result = {
        "pipeline": pipeline,
        "dataset_size": dataset_size,
        "persona_count": persona_count,
        "requirements_count": requirements_count,
        "tests_count": tests_count,
        "traceability_links": traceability_links,
        "traceability_links_breakdown": {
            "review_to_group": review_to_group,
            "group_to_persona": group_to_persona,
            "persona_to_req": persona_to_req,
            "req_to_test": req_to_test,
        },
        "review_coverage": coverage,
        "traceability_ratio": traceability_ratio,
        "testability_rate": testability_rate,
        "ambiguity_ratio": ambiguity_ratio,
    }

    cfg["output"].write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[save]  -> {cfg['output']}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", choices=["automated", "manual", "hybrid"], default="automated")
    args = parser.parse_args()
    compute(args.pipeline)
