# EECS4312_W26_SpecChain

Application: Headspace: Mindful Meditation (`com.getsomeheadspace.android`)

Application Overview:
- Headspace is a mobile wellness app focused on guided meditation, sleep support, mindfulness, and stress relief.
- Users use it to listen to meditation sessions, sleep casts, focus content, and other mental wellness exercises.
- In this project, Google Play reviews for Headspace were used as the natural language source for building personas, specifications, tests, and traceability links across the three pipelines.

Data Collection Method:
- Reviews were collected from Google Play using `google-play-scraper`.
- The collection script is in `src/01_collect_or_import.py`

Dataset:
- Original dataset: `data/reviews_raw.jsonl`
- Final cleaned dataset: `data/reviews_clean.jsonl`
- Raw review count: 5000
- Cleaned review count: 4538

Repository Structure:
- `data/` contains datasets and review groups
- `personas/` contains persona files
- `spec/` contains specifications
- `tests/` contains validation tests
- `metrics/` contains pipeline metric files
- `prompts/` contains saved automated prompts
- `src/` contains executable Python scripts
- `reflection/` contains the final reflection

Exact Commands To Run The Pipeline:
1. `python src/00_validate_repo.py`
2. `python src/02_clean.py`
3. `python src/03_manual_coding_template.py`
4. `python src/04_personas_manual.py`
5. Set `GROQ_API_KEY` in your terminal for the automated steps.
6. `python src/05_personas_auto.py`
7. `python src/06_spec_generate.py`
8. `python src/07_tests_generate.py`
9. `python src/08_metrics.py --pipeline automated`

For the metrics files:
- `python src/08_metrics.py --pipeline manual`
- `python src/08_metrics.py --pipeline hybrid`

Automated end-to-end shortcut:
- Set `GROQ_API_KEY`, then run `python src/run_all.py`
