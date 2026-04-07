"""Generate a manual persona draft from manually coded review groups."""

from __future__ import annotations

import json
from pathlib import Path


GROUPS_PATH = Path("data/review_groups_manual.json")
OUTPUT_PATH = Path("personas/personas_manual_template.json")


def persona_name_from_theme(theme: str) -> str:
    words = [word for word in theme.replace("/", " ").split() if word]
    return " ".join(word.capitalize() for word in words[:3]) or "Manual Persona"


def build_persona(group: dict, index: int) -> dict:
    theme = group.get("theme", f"Manual Theme {index}")
    group_id = group.get("group_id", f"G{index}")
    example_reviews = group.get("example_reviews", [])

    return {
        "id": f"P_manual_draft_{index}",
        "name": persona_name_from_theme(theme),
        "description": (
            f"Draft persona derived from manual review group {group_id}. "
            f"Refine this description using the evidence reviews and coding notes."
        ),
        "derived_from_group": group_id,
        "goals": [
            f"Resolve issues related to {theme.lower()}",
            "Complete core in-app tasks without confusion or interruption",
            "Receive a predictable, trustworthy experience",
        ],
        "pain_points": [
            f"Problems reflected in the theme: {theme}",
            "Current experience does not reliably support the user's main task",
            "User must rely on workarounds or support to proceed",
        ],
        "context": [
            "Derived from manually grouped Google Play reviews",
            "Represents a recurring review pattern that should be validated by the analyst",
            f"Example evidence count: {len(group.get('review_ids', []))}",
        ],
        "constraints": [
            "Replace placeholder content with analyst-authored persona details",
            "Keep every claim grounded in the evidence reviews",
            "Ensure goals and pain points map cleanly into requirements later",
        ],
        "evidence_reviews": group.get("review_ids", []),
        "example_reviews": example_reviews[:2],
    }


def main() -> None:
    groups_data = json.loads(GROUPS_PATH.read_text(encoding="utf-8"))
    groups = groups_data.get("groups", [])
    personas = [build_persona(group, idx) for idx, group in enumerate(groups, start=1)]
    OUTPUT_PATH.write_text(json.dumps({"personas": personas}, indent=2), encoding="utf-8")
    print(f"[manual-personas] Wrote draft personas to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
