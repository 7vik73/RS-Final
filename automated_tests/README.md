# ResumeIQ Automated Tests

This folder contains local automated checks for ResumeIQ.

## Fast Module Tests

```bash
cd resumeiq
venv/bin/python -m unittest discover automated_tests -p "test_*.py"
```

These tests cover parsing, preprocessing, skill extraction, scoring, analytics
math, and template rendering.

## Full 50-Resume Pipeline Checks

Offline mode:

```bash
cd resumeiq
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 venv/bin/python automated_tests/run_full_pipeline_check.py --mode offline
```

Online/cache-refresh mode:

```bash
cd resumeiq
venv/bin/python automated_tests/run_full_pipeline_check.py --mode online
```

Compare offline and online/cache-refresh summaries:

```bash
cd resumeiq
venv/bin/python automated_tests/compare_network_modes.py
```

The full check creates a temporary SQLite database, registers a recruiter,
creates a realistic backend job description, uploads all 50 synthetic PDF
resumes, runs parsing, preprocessing, skill extraction, semantic matching,
ranking, analytics, chart data generation, and dashboard rendering.

No fake dashboard analytics are created. Every assertion is based on uploaded
resume data in the temporary test database.
