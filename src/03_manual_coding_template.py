"""Create a manual review-group coding template from the cleaned dataset."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


DATASET_PATH = Path("data/reviews_clean.jsonl")
TEMPLATE_PATH = Path("data/review_groups_manual_template.json")
REVIEWS_PER_BUCKET = 12

THEME_BUCKETS = {
    "G1": {
        "theme_hint": "Subscription paywall and pricing complaints",
        "keywords": ["subscri", "price", "cost", "trial", "refund", "charge", "billing"],
    },
    "G2": {
        "theme_hint": "App crashes and performance degradation",
        "keywords": ["crash", "freeze", "slow", "glitch", "bug", "load", "stuck"],
    },
    "G3": {
        "theme_hint": "Login and account access failures",
        "keywords": ["login", "log in", "sign in", "account", "password", "authenticate"],
    },
    "G4": {
        "theme_hint": "Poor UI design and content navigation difficulty",
        "keywords": ["find", "search", "navigate", "navigation", "ui", "interface", "design"],
    },
    "G5": {
        "theme_hint": "Positive mindfulness and mental wellness experience",
        "keywords": ["love", "helpful", "calm", "sleep", "anxiety", "stress", "relax"],
    },
}


def load_reviews(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pick_groups(reviews: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for review in reviews:
        content = review.get("content", "").lower()
        for group_id, bucket in THEME_BUCKETS.items():
            if any(keyword in content for keyword in bucket["keywords"]):
                grouped[group_id].append(review)
                break
    return grouped


def build_template(groups: dict[str, list[dict]]) -> dict:
    output = {"groups": []}
    for group_id, bucket in THEME_BUCKETS.items():
        matches = sorted(
            groups.get(group_id, []),
            key=lambda row: row.get("thumbsUpCount") or 0,
            reverse=True,
        )[:REVIEWS_PER_BUCKET]

        output["groups"].append({
            "group_id": group_id,
            "theme": bucket["theme_hint"],
            "review_ids": [row["reviewId"] for row in matches],
            "example_reviews": [row.get("content", "") for row in matches[:2]],
            "manual_notes": [
                "Confirm the theme label against the listed evidence reviews.",
                "Replace any weak or off-topic review IDs before finalizing personas.",
            ],
        })
    return output


def main() -> None:
    reviews = load_reviews(DATASET_PATH)
    groups = pick_groups(reviews)
    template = build_template(groups)
    TEMPLATE_PATH.write_text(json.dumps(template, indent=2), encoding="utf-8")
    print(f"[manual-template] Wrote template to {TEMPLATE_PATH}")


if __name__ == "__main__":
    main()
