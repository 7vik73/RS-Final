"""Automated unit tests for individual ResumeIQ modules."""

import json
import tempfile
import unittest
from pathlib import Path

import app as resume_app
import utils.database as database
from ai.analytics import chart_data, dashboard_metrics, empty_charts, empty_metrics
from utils.parser import extract_candidate_name, parse_resume
from utils.preprocess import preprocess_text
from utils.scoring import calculate_resume_strength
from utils.skills import compare_skills, extract_skills, split_required_skills


class ResumeIQModuleTests(unittest.TestCase):
    """Small, fast checks for individual modules."""

    @classmethod
    def setUpClass(cls):
        cls.original_database_path = database.DATABASE_PATH
        cls.temp_dir = tempfile.TemporaryDirectory()
        database.DATABASE_PATH = Path(cls.temp_dir.name) / "test_database.db"
        database.init_database()

    @classmethod
    def tearDownClass(cls):
        database.DATABASE_PATH = cls.original_database_path
        cls.temp_dir.cleanup()

    def setUp(self):
        for table in ("candidates", "resumes", "jobs", "users"):
            database.execute(f"DELETE FROM {table}")

    def test_pdf_parser_extracts_real_sample_fields(self):
        path = Path("synthetic_visual_resumes_pdf/01_aarav_sharma_backend_python_developer.pdf")
        parsed = parse_resume(path)

        self.assertGreater(len(parsed["raw_text"]), 500)
        self.assertEqual(parsed["email"], "aarav.sharma1@example.com")
        self.assertTrue(parsed["phone"].startswith("+91"))
        self.assertIn("python", parsed["skills"])
        self.assertEqual(extract_candidate_name(path.name, parsed["raw_text"]), "Aarav Sharma")

    def test_preprocess_text_works_offline_with_fallbacks(self):
        cleaned = preprocess_text("Built REST APIs using Flask, FastAPI, and Python.")

        self.assertIn("built", cleaned)
        self.assertIn("flask", cleaned)
        self.assertIn("fastapi", cleaned)
        self.assertNotIn("and", cleaned.split())

    def test_skill_extraction_and_overlap(self):
        resume_skills = extract_skills("Python Flask FastAPI Docker Git PostgreSQL")
        required = split_required_skills("python, flask, docker, react")
        overlap, missing, score = compare_skills(resume_skills, required)

        self.assertEqual(overlap, ["docker", "flask", "python"])
        self.assertEqual(missing, ["react"])
        self.assertAlmostEqual(score, 0.75)

    def test_resume_strength_score_uses_real_sections(self):
        sections = {
            "experience": "Built APIs",
            "projects": "ResumeIQ project",
            "education": "B.Tech",
            "certifications": "Python certificate",
        }
        score = calculate_resume_strength("email@example.com " + ("word " * 220), ["python"] * 8, sections)

        self.assertGreaterEqual(score, 8)
        self.assertLessEqual(score, 10)

    def test_empty_analytics_are_safe(self):
        metrics = empty_metrics()
        charts = empty_charts()

        self.assertEqual(metrics["total_resumes"], 0)
        self.assertEqual(charts["matchDistribution"]["labels"][0], "0-20%")
        self.assertEqual(sum(charts["matchDistribution"]["values"]), 0)

    def test_analytics_aggregate_only_database_rows(self):
        user_id = database.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("tester", "hash"),
        )
        job_id = database.execute(
            "INSERT INTO jobs (user_id, title, description, required_skills) VALUES (?, ?, ?, ?)",
            (user_id, "Backend", "Python Flask APIs", "python, flask, docker"),
        )
        resume_id = database.execute(
            """
            INSERT INTO resumes
                (user_id, job_id, filename, stored_path, raw_text, cleaned_text, email, phone, skills, sections)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                job_id,
                "candidate.pdf",
                "candidate.pdf",
                "Python Flask resume",
                "python flask resume",
                "candidate@example.com",
                "+91 98000 00000",
                "python, flask",
                json.dumps({"experience": "Flask APIs", "projects": "Backend project"}),
            ),
        )
        database.execute(
            """
            INSERT INTO candidates
                (resume_id, job_id, candidate_name, semantic_score, skill_score,
                 experience_score, project_score, resume_strength, final_score,
                 overlap_skills, missing_skills, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resume_id,
                job_id,
                "Test Candidate",
                0.8,
                0.66,
                0.7,
                0.6,
                8.0,
                73.5,
                "python, flask",
                "docker",
                "Pending",
            ),
        )

        metrics = dashboard_metrics(job_id)
        charts = chart_data(job_id)

        self.assertEqual(metrics["total_resumes"], 1)
        self.assertEqual(metrics["most_missing_skill"], "docker")
        self.assertEqual(metrics["average_semantic"], 80)
        self.assertEqual(sum(charts["matchDistribution"]["values"]), 1)
        self.assertEqual(sum(charts["semanticDistribution"]["values"]), 1)
        self.assertEqual(charts["statusDistribution"]["values"], [1, 0, 0])

    def test_dashboard_template_renders_analytics_sections(self):
        with resume_app.app.test_request_context("/dashboard?job_id=1"):
            html = resume_app.app.jinja_env.get_template("dashboard.html").render(
                jobs=[],
                selected_job={"id": 1, "title": "Backend", "description": "Python APIs"},
                candidates=[],
                metrics=empty_metrics(),
                charts=json.dumps(empty_charts()),
                filters={},
            )

        self.assertIn("Average Skill Match", html)
        self.assertIn("Candidate Match Score Distribution", html)
        self.assertIn("AI Insight Panel", html)

    def test_recruiter_can_delete_job_and_related_rows(self):
        with resume_app.app.test_client() as client:
            client.post("/register", data={"username": "deleter", "password": "pass123"})
            client.post("/login", data={"username": "deleter", "password": "pass123"})
            response = client.post(
                "/jobs",
                data={
                    "title": "Delete Test",
                    "description": "Python Flask APIs",
                    "required_skills": "python, flask",
                },
                follow_redirects=False,
            )
            job_id = int(response.headers["Location"].split("job_id=")[1])
            user_id = database.fetch_one("SELECT id FROM users WHERE username = ?", ("deleter",))["id"]

            resume_id = database.execute(
                """
                INSERT INTO resumes
                    (user_id, job_id, filename, stored_path, raw_text, cleaned_text, email, phone, skills, sections)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    job_id,
                    "delete.pdf",
                    "uploads/delete.pdf",
                    "Python Flask",
                    "python flask",
                    "delete@example.com",
                    "+91 98000 00001",
                    "python, flask",
                    "{}",
                ),
            )
            database.execute(
                "INSERT INTO candidates (resume_id, job_id, candidate_name) VALUES (?, ?, ?)",
                (resume_id, job_id, "Delete Candidate"),
            )

            delete_response = client.post(f"/jobs/{job_id}/delete", follow_redirects=True)

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(database.fetch_one("SELECT COUNT(*) AS count FROM jobs WHERE id = ?", (job_id,))["count"], 0)
        self.assertEqual(database.fetch_one("SELECT COUNT(*) AS count FROM resumes WHERE job_id = ?", (job_id,))["count"], 0)
        self.assertEqual(database.fetch_one("SELECT COUNT(*) AS count FROM candidates WHERE job_id = ?", (job_id,))["count"], 0)


if __name__ == "__main__":
    unittest.main()
