"""
05_personas_auto.py
===================
Automated pipeline: reviews -> grouped clusters -> LLM-labelled themes -> personas.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

from groq import Groq
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
N_CLUSTERS = 5
REVIEWS_PER_CALL = 12
REVIEWS_PER_GROUP = 10
EVIDENCE_PER_PERSONA = 6
MAX_REVIEW_CHARS = 220
TFIDF_MAX_FEATURES = 1000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 2
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 20
STRATIFY_PER_SCORE = 60

DATASET_PATH = Path("data/reviews_clean.jsonl")
GROUPS_PATH = Path("data/review_groups_auto.json")
PERSONAS_PATH = Path("personas/personas_auto.json")
PROMPTS_PATH = Path("prompts/prompt_auto.json")

THEME_PROMPT_TEMPLATE = """\
You are a software requirements analyst studying user reviews of the Headspace meditation app on Android.
Below are {n} user reviews that have been grouped together by a TF-IDF + KMeans clustering algorithm because
they share similar vocabulary and topics.

Reviews:
{reviews}

Task:
Identify the single dominant theme that unifies these reviews. Respond only with valid JSON in this format:

{{
  "theme": "<concise theme name, 4-8 words>",
  "rationale": "<one sentence explaining what the reviews share>"
}}
"""

PERSONA_PROMPT_TEMPLATE = """\
You are a software requirements analyst. Below is a group of user reviews of the Headspace meditation app
on Android. The group has been labelled with the theme: "{theme}".

Reviews:
{reviews}

Task:
Create a structured user persona representing the kind of user who wrote these reviews. Respond only with
valid JSON in this format:

{{
  "name": "<persona name, 2-4 words>",
  "description": "<2-3 sentence description>",
  "goals": ["<goal 1>", "<goal 2>", "<goal 3>"],
  "pain_points": ["<pain 1>", "<pain 2>", "<pain 3>", "<pain 4>"],
  "context": ["<context 1>", "<context 2>", "<context 3>"],
  "constraints": ["<constraint 1>", "<constraint 2>", "<constraint 3>"]
}}
"""


def load_reviews(path: Path) -> list[dict]:
    reviews = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                reviews.append(json.loads(line))
    print(f"[load] {len(reviews)} reviews loaded from {path}")
    return reviews


def stratified_sample(reviews: list[dict], per_score: int = STRATIFY_PER_SCORE) -> list[dict]:
    by_score: dict[int, list[dict]] = defaultdict(list)
    for review in reviews:
        by_score[review["score"]].append(review)

    sample = []
    for score in sorted(by_score):
        bucket = sorted(
            by_score[score],
            key=lambda row: row.get("thumbsUpCount") or 0,
            reverse=True,
        )
        sample.extend(bucket[:per_score])

    print(f"[sample] {len(sample)} reviews sampled ({per_score} per star rating x {len(by_score)} ratings)")
    return sample


def cluster_reviews(sample: list[dict], n_clusters: int = N_CLUSTERS) -> dict[int, list[int]]:
    texts = [review["cleaned_content"] for review in sample]
    vectorizer = TfidfVectorizer(
        max_features=TFIDF_MAX_FEATURES,
        ngram_range=TFIDF_NGRAM_RANGE,
        min_df=TFIDF_MIN_DF,
    )
    matrix = vectorizer.fit_transform(texts)
    print(f"[tfidf] TF-IDF matrix: {matrix.shape[0]} docs x {matrix.shape[1]} features")

    model = KMeans(
        n_clusters=n_clusters,
        random_state=KMEANS_RANDOM_STATE,
        n_init=KMEANS_N_INIT,
    )
    labels = model.fit_predict(matrix)

    clusters: dict[int, list[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        clusters[int(label)].append(index)

    for cluster_id, members in sorted(clusters.items()):
        print(f"  cluster {cluster_id}: {len(members)} reviews")

    return dict(clusters)


def pick_representatives(cluster_indexes: list[int], sample: list[dict], k: int = REVIEWS_PER_CALL) -> list[dict]:
    ranked = sorted(
        cluster_indexes,
        key=lambda index: len(sample[index].get("content", "")),
        reverse=True,
    )
    return [sample[index] for index in ranked[:k]]


def groq_call(client: Groq, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            wait = 2 ** attempt
            print(f"  [groq] attempt {attempt + 1} failed: {exc}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Groq API call failed after {retries} attempts.")


def parse_json_response(raw: str) -> dict:
    clean = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(clean)


def build_review_block(representatives: list[dict], max_chars: int = MAX_REVIEW_CHARS) -> str:
    lines = []
    for review in representatives:
        text = review.get("content", "").replace("\n", " ")[:max_chars]
        lines.append(f'- "{text}"')
    return "\n".join(lines)


def run_pipeline() -> None:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        sys.exit("Error: GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)
    print(f"[init] Groq client ready, model: {GROQ_MODEL}")

    GROUPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PERSONAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROMPTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_reviews = load_reviews(DATASET_PATH)
    sample = stratified_sample(all_reviews)

    print(f"\n[cluster] Clustering {len(sample)} reviews into {N_CLUSTERS} groups...")
    clusters = cluster_reviews(sample, n_clusters=N_CLUSTERS)

    prompts_record = {
        "model": GROQ_MODEL,
        "theme_prompt_template": THEME_PROMPT_TEMPLATE,
        "persona_prompt_template": PERSONA_PROMPT_TEMPLATE,
        "parameters": {
            "reviews_per_call": REVIEWS_PER_CALL,
            "max_review_chars": MAX_REVIEW_CHARS,
            "temperature": 0.3,
            "max_tokens": 800,
        },
    }
    PROMPTS_PATH.write_text(json.dumps(prompts_record, indent=2), encoding="utf-8")
    print(f"\n[prompts] Saved prompt templates -> {PROMPTS_PATH}")

    groups_out = {"groups": []}
    personas_out = {"personas": []}

    for cluster_index, (cluster_id, member_indexes) in enumerate(sorted(clusters.items())):
        group_id = f"A{cluster_index + 1}"
        persona_id = f"P_auto_{cluster_index + 1}"
        print(f"\n[cluster {cluster_id}] {len(member_indexes)} reviews -> group {group_id}")

        representatives = pick_representatives(member_indexes, sample, k=REVIEWS_PER_CALL)
        review_block = build_review_block(representatives)

        print("  [groq] Calling LLM for theme label...")
        theme_raw = groq_call(client, THEME_PROMPT_TEMPLATE.format(n=len(representatives), reviews=review_block))
        theme_parsed = parse_json_response(theme_raw)
        theme = theme_parsed.get("theme", "Unknown theme")
        rationale = theme_parsed.get("rationale", "")
        print(f"  -> theme: {theme}")

        sorted_indexes = sorted(
            member_indexes,
            key=lambda index: len(sample[index].get("content", "")),
            reverse=True,
        )
        selected_ids = [sample[index]["reviewId"] for index in sorted_indexes[:REVIEWS_PER_GROUP]]
        example_contents = [sample[index]["content"] for index in sorted_indexes[:2]]

        groups_out["groups"].append({
            "group_id": group_id,
            "theme": theme,
            "review_ids": selected_ids,
            "example_reviews": example_contents,
            "cluster_rationale": rationale,
            "source_cluster": f"kmeans_cluster_{cluster_id}",
            "cluster_size": len(member_indexes),
        })

        print("  [groq] Calling LLM for persona generation...")
        persona_raw = groq_call(client, PERSONA_PROMPT_TEMPLATE.format(theme=theme, reviews=review_block))
        persona_parsed = parse_json_response(persona_raw)
        print(f"  -> persona name: {persona_parsed.get('name', '?')}")

        evidence = [sample[index]["reviewId"] for index in sorted_indexes[:EVIDENCE_PER_PERSONA]]
        personas_out["personas"].append({
            "id": persona_id,
            "name": persona_parsed.get("name", "Unknown Persona"),
            "description": persona_parsed.get("description", ""),
            "derived_from_group": group_id,
            "goals": persona_parsed.get("goals", []),
            "pain_points": persona_parsed.get("pain_points", []),
            "context": persona_parsed.get("context", []),
            "constraints": persona_parsed.get("constraints", []),
            "evidence_reviews": evidence,
            "generation_method": "automated",
            "source_cluster": f"kmeans_cluster_{cluster_id}",
        })

    GROUPS_PATH.write_text(json.dumps(groups_out, indent=2), encoding="utf-8")
    PERSONAS_PATH.write_text(json.dumps(personas_out, indent=2), encoding="utf-8")
    print(f"\n[save] review groups -> {GROUPS_PATH}")
    print(f"[save] personas       -> {PERSONAS_PATH}")
    print("\nAutomated pipeline complete.")
    print(f"  {len(groups_out['groups'])} groups, {len(personas_out['personas'])} personas produced.")


if __name__ == "__main__":
    run_pipeline()
