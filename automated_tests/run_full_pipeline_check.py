"""Run a full ResumeIQ pipeline check with all 50 synthetic PDF resumes.

This script intentionally exercises the real Flask upload flow and real
Sentence Transformer semantic scoring. It uses a temporary SQLite database so
normal recruiter data is never touched.
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def configure_mode(mode):
    """Set network/cache behavior before importing the app and model modules."""
    if mode == "offline":
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    else:
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("TRANSFORMERS_OFFLINE", None)


def run_check(mode, limit=None):
    configure_mode(mode)

    import app as resume_app
    import utils.database as database
    from ai.analytics import chart_data, dashboard_metrics

    files = sorted((ROOT / "synthetic_visual_resumes_pdf").glob("*.pdf"))
    if limit:
        files = files[:limit]
    if not files:
        raise AssertionError("No synthetic PDF resumes found.")

    original_database_path = database.DATABASE_PATH
    with tempfile.TemporaryDirectory() as temp_dir:
        database.DATABASE_PATH = Path(temp_dir) / f"pipeline_{mode}.db"
        database.init_database()

        with resume_app.app.test_client() as client:
            username = f"pipeline_{mode}_recruiter"
            client.post("/register", data={"username": username, "password": "pass123"}, follow_redirects=True)
            client.post("/login", data={"username": username, "password": "pass123"}, follow_redirects=True)

            response = client.post(
                "/jobs",
                data={
                    "title": "Backend API Developer",
                    "description": (
                        "Build REST APIs using Python, Flask, FastAPI, SQLite, "
                        "PostgreSQL, Docker, Git, cloud deployment, and backend service design."
                    ),
                    "required_skills": "python, flask, fastapi, sqlite, postgresql, docker, git",
                },
                follow_redirects=False,
            )
            job_id = int(response.headers["Location"].split("job_id=")[1])

            handles = []
            upload_data = []
            try:
                for path in files:
                    handle = open(path, "rb")
                    handles.append(handle)
                    upload_data.append((handle, path.name))

                upload_response = client.post(
                    f"/upload/{job_id}",
                    data={"resumes": upload_data},
                    content_type="multipart/form-data",
                    follow_redirects=True,
                )
            finally:
                for handle in handles:
                    handle.close()

            assert upload_response.status_code == 200

            candidate_count = database.fetch_one(
                "SELECT COUNT(*) AS count FROM candidates WHERE job_id = ?",
                (job_id,),
            )["count"]
            assert candidate_count == len(files), f"Expected {len(files)} candidates, got {candidate_count}"

            rows = database.fetch_all(
                """
                SELECT candidates.*, resumes.email, resumes.phone, resumes.skills
                FROM candidates
                JOIN resumes ON resumes.id = candidates.resume_id
                WHERE candidates.job_id = ?
                """,
                (job_id,),
            )
            assert all(row["email"] for row in rows)
            assert all(row["phone"] for row in rows)
            assert all(row["final_score"] is not None for row in rows)
            assert all(0 <= row["final_score"] <= 100 for row in rows)
            assert all(0 <= row["semantic_score"] <= 1 for row in rows)
            assert all(0 <= row["skill_score"] <= 1 for row in rows)
            assert all(0 <= row["experience_score"] <= 1 for row in rows)
            assert all(0 <= row["project_score"] <= 1 for row in rows)
            assert all(0 <= row["resume_strength"] <= 10 for row in rows)

            metrics = dashboard_metrics(job_id)
            charts = chart_data(job_id)
            assert metrics["total_resumes"] == len(files)
            assert 0 <= metrics["average_score"] <= 100
            assert 0 <= metrics["average_semantic"] <= 100
            assert 0 <= metrics["average_skill_match"] <= 100
            assert 0 <= metrics["average_completeness"] <= 100
            assert metrics["top_candidate_name"] != "No candidates yet"
            assert len(metrics["insights"]) >= 3

            assert sum(charts["matchDistribution"]["values"]) == len(files)
            assert sum(charts["semanticDistribution"]["values"]) == len(files)
            assert sum(charts["statusDistribution"]["values"]) == len(files)
            assert sum(charts["domainDistribution"]["values"]) == len(files)
            assert charts["topSkills"]["labels"]
            assert charts["topSkills"]["values"]

            html = client.get(f"/dashboard?job_id={job_id}").data.decode()
            required_strings = [
                "Average Skill Match",
                "Most Missing Skill",
                "Candidate Match Score Distribution",
                "Semantic Relevance Distribution",
                "Top Detected Skills",
                "Domain Distribution",
                "Shortlisted vs Rejected",
                "AI Insight Panel",
                "Skill Match %",
            ]
            for text in required_strings:
                assert text in html, f"Missing dashboard text: {text}"

            summary = {
                "mode": mode,
                "job_id": job_id,
                "resumes_uploaded": len(files),
                "candidates_created": candidate_count,
                "average_match": metrics["average_score"],
                "average_semantic": metrics["average_semantic"],
                "average_skill_match": metrics["average_skill_match"],
                "top_skill": metrics["top_skill"],
                "most_missing_skill": metrics["most_missing_skill"],
                "top_candidate": metrics["top_candidate_name"],
                "match_distribution_total": sum(charts["matchDistribution"]["values"]),
                "semantic_distribution_total": sum(charts["semanticDistribution"]["values"]),
                "domain_distribution_total": sum(charts["domainDistribution"]["values"]),
            }

        database.DATABASE_PATH = original_database_path

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["offline", "online"], default="offline")
    parser.add_argument("--limit", type=int, default=None, help="Optional smaller run for quick debugging.")
    args = parser.parse_args()

    summary = run_check(args.mode, args.limit)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
