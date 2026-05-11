"""Generate sample ResumeIQ metric outputs for curated resume/job combinations."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as resume_app
import utils.database as database
from ai.analytics import chart_data, dashboard_metrics


RESUME_DIR = ROOT / "synthetic_visual_resumes_pdf"


CASES = [
    {
        "name": "Backend API Hiring",
        "description": "Build REST APIs using Python, Flask, FastAPI, PostgreSQL, SQLite, Docker, Git, and backend service design.",
        "required_skills": "python, flask, fastapi, postgresql, sqlite, docker, git",
        "roles": [
            "backend_python_developer",
            "full_stack_engineer",
            "devops_engineer",
            "cloud_engineer",
            "data_scientist",
            "graphic_designer",
        ],
    },
    {
        "name": "Frontend Product UI Hiring",
        "description": "Create responsive frontend interfaces using React Js, Next Js, TypeScript, Tailwind, HTML, CSS, accessibility, and Figma collaboration.",
        "required_skills": "react js, next js, typescript, tailwind, html, css, accessibility, figma",
        "roles": [
            "frontend_react_developer",
            "full_stack_engineer",
            "ui_ux_designer",
            "mobile_app_developer",
            "content_writer",
            "backend_python_developer",
        ],
    },
    {
        "name": "Data Science Analytics Hiring",
        "description": "Analyze business data with Python, SQL, pandas, numpy, machine learning, scikit-learn, NLP, Tableau, Power BI, and dashboards.",
        "required_skills": "python, sql, pandas, numpy, machine learning, scikit-learn, nlp, tableau, power bi",
        "roles": [
            "data_analyst",
            "data_scientist",
            "machine_learning_engineer",
            "nlp_engineer",
            "finance_analyst",
            "graphic_designer",
        ],
    },
    {
        "name": "DevOps Cloud Hiring",
        "description": "Manage AWS cloud infrastructure, Docker, Kubernetes, Linux, Terraform, CI/CD, monitoring, networking, and incident response.",
        "required_skills": "aws, docker, kubernetes, linux, terraform, ci/cd, monitoring, networking",
        "roles": [
            "devops_engineer",
            "cloud_engineer",
            "cybersecurity_analyst",
            "database_administrator",
            "backend_python_developer",
            "sales_executive",
        ],
    },
    {
        "name": "Business Product Operations Hiring",
        "description": "Drive requirements gathering, stakeholder management, agile delivery, roadmap planning, Jira tracking, analytics, process improvement, and reporting.",
        "required_skills": "requirements gathering, stakeholder management, agile, roadmap, jira, analytics, process improvement, reporting",
        "roles": [
            "business_analyst",
            "project_manager",
            "product_manager",
            "operations_manager",
            "hr_recruiter",
            "finance_analyst",
        ],
    },
]


def find_resume(role, offset=0):
    matches = sorted(RESUME_DIR.glob(f"*_{role}.pdf"))
    if not matches:
        raise FileNotFoundError(f"No resume found for role: {role}")
    return matches[offset % len(matches)]


def create_case(client, case, case_index):
    response = client.post(
        "/jobs",
        data={
            "title": case["name"],
            "description": case["description"],
            "required_skills": case["required_skills"],
        },
        follow_redirects=False,
    )
    job_id = int(response.headers["Location"].split("job_id=")[1])

    handles = []
    upload_data = []
    try:
        for index, role in enumerate(case["roles"]):
            path = find_resume(role, offset=case_index)
            handle = open(path, "rb")
            handles.append(handle)
            upload_data.append((handle, path.name))
        client.post(
            f"/upload/{job_id}",
            data={"resumes": upload_data},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
    finally:
        for handle in handles:
            handle.close()

    candidates = database.fetch_all(
        """
        SELECT candidate_name, final_score, semantic_score, skill_score,
               experience_score, project_score, resume_strength, overlap_skills, missing_skills
        FROM candidates
        WHERE job_id = ?
        ORDER BY final_score DESC
        """,
        (job_id,),
    )
    metrics = dashboard_metrics(job_id)
    charts = chart_data(job_id)

    return {
        "case": case["name"],
        "resumes": [Path(item[1]).name for item in upload_data],
        "metrics": {
            "total_resumes": metrics["total_resumes"],
            "average_match": metrics["average_score"],
            "average_semantic": metrics["average_semantic"],
            "average_skill_match": metrics["average_skill_match"],
            "top_skill": metrics["top_skill"],
            "most_missing_skill": metrics["most_missing_skill"],
            "top_candidate": metrics["top_candidate_name"],
            "top_candidate_score": metrics["top_candidate_score"],
        },
        "chart_totals": {
            "match_distribution": sum(charts["matchDistribution"]["values"]),
            "semantic_distribution": sum(charts["semanticDistribution"]["values"]),
            "domain_distribution": sum(charts["domainDistribution"]["values"]),
        },
        "top_3_candidates": [
            {
                "name": resume_app.clean_candidate_name(row["candidate_name"]),
                "match": round(row["final_score"] or 0, 2),
                "semantic": round((row["semantic_score"] or 0) * 100, 2),
                "skill_match": round((row["skill_score"] or 0) * 100, 2),
                "experience": round((row["experience_score"] or 0) * 100, 2),
                "project": round((row["project_score"] or 0) * 100, 2),
                "strength": round((row["resume_strength"] or 0) * 10, 2),
                "matched": row["overlap_skills"],
                "missing": row["missing_skills"],
            }
            for row in candidates[:3]
        ],
    }


def main():
    original_database_path = database.DATABASE_PATH
    with tempfile.TemporaryDirectory() as temp_dir:
        database.DATABASE_PATH = Path(temp_dir) / "sample_cases.db"
        database.init_database()

        with resume_app.app.test_client() as client:
            client.post("/register", data={"username": "case_runner", "password": "pass123"})
            client.post("/login", data={"username": "case_runner", "password": "pass123"})
            results = [create_case(client, case, index) for index, case in enumerate(CASES)]

        database.DATABASE_PATH = original_database_path

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
