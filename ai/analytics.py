"""Recruiter analytics built only from uploaded resumes and stored scores."""

from collections import Counter

from utils.database import fetch_all, fetch_one


SCORE_BUCKETS = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]

DOMAIN_RULES = {
    "Backend Development": {"python", "flask", "fastapi", "django", "api", "rest api", "postgresql", "sqlite"},
    "Frontend Development": {"javascript", "typescript", "react", "angular", "vue", "tailwind", "html", "css"},
    "Full Stack": {"python", "javascript", "flask", "react", "nodejs", "sqlite"},
    "Data Science": {"machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "nlp"},
    "DevOps and Cloud": {"docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd", "linux"},
    "Mobile Development": {"kotlin", "swift", "flutter", "firebase", "mobile ui"},
    "Design": {"figma", "photoshop", "illustrator", "wireframes", "prototyping", "branding"},
    "Marketing": {"seo", "google analytics", "content marketing", "social media", "email marketing"},
    "Business and Product": {"requirements gathering", "stakeholder management", "roadmap", "agile", "scrum"},
    "Operations and Support": {"customer service", "ticketing", "process improvement", "vendor management", "inventory"},
}

GENERIC_ANALYTICS_SKILLS = {
    "communication",
    "documentation",
    "reporting",
    "stakeholder communication",
    "planning",
}


def empty_metrics():
    """Default analytics state before any resume is uploaded."""
    return {
        "total_resumes": 0,
        "average_score": 0,
        "average_semantic": 0,
        "average_skill_match": 0,
        "shortlisted": 0,
        "top_skill": "No skills yet",
        "most_missing_skill": "No missing skills yet",
        "average_completeness": 0,
        "average_experience": 0,
        "average_project": 0,
        "top_candidate_name": "No candidates yet",
        "top_candidate_score": 0,
        "insights": ["Upload resumes to generate recruiter insights from real candidate data."],
    }


def empty_charts():
    """Default Chart.js state before any resume is uploaded."""
    empty_distribution = {"labels": SCORE_BUCKETS, "values": [0, 0, 0, 0, 0]}
    return {
        "matchDistribution": empty_distribution,
        "semanticDistribution": empty_distribution,
        "topSkills": {"labels": [], "values": []},
        "domainDistribution": {"labels": [], "values": []},
        "statusDistribution": {"labels": ["Pending", "Shortlisted", "Rejected"], "values": [0, 0, 0]},
    }


def dashboard_metrics(job_id):
    """Aggregate recruiter metrics from SQLite records."""
    candidates = _candidate_rows(job_id)
    if not candidates:
        return empty_metrics()

    skill_counter = _skill_counter(candidates)
    recruiter_skill_counter = _recruiter_skill_counter(candidates)
    missing_counter = _missing_skill_counter(candidates)
    top_candidate = max(candidates, key=lambda row: row["final_score"] or 0)

    insights = _build_insights(candidates, skill_counter, missing_counter)

    return {
        "total_resumes": len(candidates),
        "average_score": _average_percent(row["final_score"] for row in candidates),
        "average_semantic": _average_decimal_percent(row["semantic_score"] for row in candidates),
        "average_skill_match": _average_decimal_percent(row["skill_score"] for row in candidates),
        "shortlisted": sum(1 for row in candidates if row["status"] == "Shortlisted"),
        "top_skill": recruiter_skill_counter.most_common(1)[0][0] if recruiter_skill_counter else "No skills yet",
        "most_missing_skill": missing_counter.most_common(1)[0][0] if missing_counter else "No missing skills yet",
        "average_completeness": _average_percent((row["resume_strength"] or 0) * 10 for row in candidates),
        "average_experience": _average_decimal_percent(row["experience_score"] for row in candidates),
        "average_project": _average_decimal_percent(row["project_score"] for row in candidates),
        "top_candidate_name": _clean_candidate_name(top_candidate["candidate_name"]),
        "top_candidate_score": round(top_candidate["final_score"] or 0, 2),
        "insights": insights,
    }


def chart_data(job_id):
    """Prepare Chart.js friendly arrays for the dashboard."""
    candidates = _candidate_rows(job_id)
    if not candidates:
        return empty_charts()

    skill_counter = _recruiter_skill_counter(candidates)
    domain_counter = _domain_counter(candidates)
    status_counter = Counter(row["status"] or "Pending" for row in candidates)

    top_skills = skill_counter.most_common(10)

    return {
        "matchDistribution": _bucket_scores(row["final_score"] for row in candidates),
        "semanticDistribution": _bucket_scores((row["semantic_score"] or 0) * 100 for row in candidates),
        "topSkills": {
            "labels": [skill.title() for skill, _ in top_skills],
            "values": [count for _, count in top_skills],
        },
        "domainDistribution": {
            "labels": [domain for domain, _ in domain_counter.most_common()],
            "values": [count for _, count in domain_counter.most_common()],
        },
        "statusDistribution": {
            "labels": ["Pending", "Shortlisted", "Rejected"],
            "values": [
                status_counter.get("Pending", 0),
                status_counter.get("Shortlisted", 0),
                status_counter.get("Rejected", 0),
            ],
        },
    }


def _candidate_rows(job_id):
    return fetch_all(
        """
        SELECT
            candidates.*,
            resumes.skills
        FROM candidates
        JOIN resumes ON resumes.id = candidates.resume_id
        WHERE candidates.job_id = ?
        ORDER BY candidates.final_score DESC
        """,
        (job_id,),
    )


def _split_csv(value):
    return [item.strip().lower() for item in (value or "").split(",") if item.strip()]


def _clean_candidate_name(name):
    name = name or "Unknown Candidate"
    lowered = name.lower()
    if lowered.startswith("contact "):
        return name[8:].strip()
    return name


def _skill_counter(candidates):
    counter = Counter()
    for row in candidates:
        counter.update(_split_csv(row["skills"]))
    return counter


def _recruiter_skill_counter(candidates):
    counter = _skill_counter(candidates)
    for skill in GENERIC_ANALYTICS_SKILLS:
        counter.pop(skill, None)
    return counter


def _missing_skill_counter(candidates):
    counter = Counter()
    for row in candidates:
        counter.update(_split_csv(row["missing_skills"]))
    return counter


def _domain_counter(candidates):
    counter = Counter()
    for row in candidates:
        skills = set(_split_csv(row["skills"]))
        best_domain = "General"
        best_score = 0
        for domain, domain_skills in DOMAIN_RULES.items():
            score = len(skills.intersection(domain_skills))
            if score > best_score:
                best_domain = domain
                best_score = score
        counter[best_domain] += 1
    return counter


def _bucket_scores(scores):
    buckets = dict.fromkeys(SCORE_BUCKETS, 0)
    for score in scores:
        score = max(0, min(100, score or 0))
        if score < 20:
            buckets["0-20%"] += 1
        elif score < 40:
            buckets["20-40%"] += 1
        elif score < 60:
            buckets["40-60%"] += 1
        elif score < 80:
            buckets["60-80%"] += 1
        else:
            buckets["80-100%"] += 1
    return {"labels": list(buckets.keys()), "values": list(buckets.values())}


def _average_percent(values):
    values = [value or 0 for value in values]
    if not values:
        return 0
    return round(sum(values) / len(values), 2)


def _average_decimal_percent(values):
    return _average_percent((value or 0) * 100 for value in values)


def _build_insights(candidates, skill_counter, missing_counter):
    insights = []
    total = len(candidates)
    domain_counter = _domain_counter(candidates)
    top_domain = domain_counter.most_common(1)[0][0] if domain_counter else None
    strong_count = sum(1 for row in candidates if (row["final_score"] or 0) >= 70)
    strong_percent = round((strong_count / total) * 100) if total else 0
    avg_semantic = _average_decimal_percent(row["semantic_score"] for row in candidates)

    if top_domain:
        insights.append(f"Most applicants are {top_domain.lower()} focused.")
    if missing_counter:
        insights.append(f"{missing_counter.most_common(1)[0][0].title()} is the most commonly missing skill.")
    insights.append(f"{strong_percent}% of resumes scored at least 70% overall match.")
    if avg_semantic >= 70:
        insights.append("Average semantic relevance is high for this job requirement.")
    elif avg_semantic >= 45:
        insights.append("Average semantic relevance is moderate; review top candidates closely.")
    else:
        insights.append("Average semantic relevance is low; the applicant pool may not match this requirement well.")
    if skill_counter:
        insights.append(f"{skill_counter.most_common(1)[0][0].title()} is the most common detected skill.")
    return insights
