"""Analytics built only from uploaded resumes and stored candidate scores."""

from collections import Counter

from utils.database import fetch_all, fetch_one


def dashboard_metrics(job_id):
    """Aggregate recruiter metrics from SQLite records."""
    totals = fetch_one(
        """
        SELECT
            COUNT(*) AS total_resumes,
            COALESCE(AVG(final_score), 0) AS average_score,
            SUM(CASE WHEN status = 'Shortlisted' THEN 1 ELSE 0 END) AS shortlisted
        FROM candidates
        WHERE job_id = ?
        """,
        (job_id,),
    )

    skill_rows = fetch_all(
        """
        SELECT resumes.skills
        FROM resumes
        JOIN candidates ON candidates.resume_id = resumes.id
        WHERE candidates.job_id = ?
        """,
        (job_id,),
    )

    skill_counter = Counter()
    for row in skill_rows:
        for skill in (row["skills"] or "").split(","):
            cleaned = skill.strip()
            if cleaned:
                skill_counter[cleaned] += 1

    top_skill = skill_counter.most_common(1)[0][0] if skill_counter else "No skills yet"

    return {
        "total_resumes": totals["total_resumes"] or 0,
        "average_score": round(totals["average_score"] or 0, 2),
        "shortlisted": totals["shortlisted"] or 0,
        "top_skill": top_skill,
    }


def chart_data(job_id):
    """Prepare Chart.js friendly arrays for the dashboard."""
    candidates = fetch_all(
        """
        SELECT final_score, semantic_score
        FROM candidates
        WHERE job_id = ?
        ORDER BY final_score DESC
        """,
        (job_id,),
    )

    resumes = fetch_all(
        """
        SELECT resumes.skills
        FROM resumes
        JOIN candidates ON candidates.resume_id = resumes.id
        WHERE candidates.job_id = ?
        """,
        (job_id,),
    )

    skill_counter = Counter()
    for resume in resumes:
        for skill in (resume["skills"] or "").split(","):
            cleaned = skill.strip()
            if cleaned:
                skill_counter[cleaned] += 1

    score_buckets = {"0-39": 0, "40-59": 0, "60-79": 0, "80-100": 0}
    semantic_scores = []

    for candidate in candidates:
        score = candidate["final_score"]
        semantic_scores.append(round(candidate["semantic_score"] * 100, 2))
        if score < 40:
            score_buckets["0-39"] += 1
        elif score < 60:
            score_buckets["40-59"] += 1
        elif score < 80:
            score_buckets["60-79"] += 1
        else:
            score_buckets["80-100"] += 1

    top_skills = skill_counter.most_common(8)

    return {
        "matchDistribution": {
            "labels": list(score_buckets.keys()),
            "values": list(score_buckets.values()),
        },
        "topSkills": {
            "labels": [skill for skill, _ in top_skills],
            "values": [count for _, count in top_skills],
        },
        "semanticScores": {
            "labels": [f"Candidate {index + 1}" for index in range(len(semantic_scores))],
            "values": semantic_scores,
        },
    }
