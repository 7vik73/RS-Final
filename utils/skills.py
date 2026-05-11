"""Keyword and regex based skill extraction.

This module does not train a model. It uses transparent skill dictionaries so
recruiters and evaluators can understand exactly how skills are detected.
"""

import re


SKILL_DICTIONARY = {
    "Programming": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "sql", "r", "go", "golang", "php", "ruby", "kotlin", "swift",
    ],
    "Frameworks": [
        "flask", "django", "fastapi", "react", "react js", "angular", "vue",
        "node.js", "node js", "nodejs", "express", "express js", "next.js",
        "next js", "nextjs", "spring", "spring boot", "tailwind", "bootstrap",
    ],
    "Databases": [
        "sqlite", "mysql", "postgresql", "mongodb", "redis", "oracle",
        "sql server", "firebase",
    ],
    "Cloud": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "heroku", "vercel", "netlify",
    ],
    "Tools": [
        "git", "github", "gitlab", "jira", "linux", "postman", "figma",
        "power bi", "tableau", "excel", "wordpress", "crm", "ats", "selenium",
    ],
    "AI and Data": [
        "machine learning", "deep learning", "nlp", "nltk", "pandas",
        "numpy", "scikit-learn", "tensorflow", "pytorch", "matplotlib",
        "sentence transformers", "transformers",
    ],
    "Design": [
        "photoshop", "illustrator", "branding", "layout design", "typography",
        "wireframes", "prototyping", "user research", "design systems",
        "usability testing", "accessibility", "creative assets",
    ],
    "Marketing": [
        "seo", "google analytics", "content marketing", "social media",
        "email marketing", "campaigns", "copywriting", "editing",
        "blog writing", "content strategy", "market research",
    ],
    "Business": [
        "requirements gathering", "stakeholder management", "process mapping",
        "documentation", "agile", "scrum", "risk management", "planning",
        "stakeholder communication", "reporting", "roadmap", "analytics",
        "prioritization", "stakeholders",
    ],
    "HR and Operations": [
        "recruitment", "screening", "interviewing", "onboarding",
        "communication", "process improvement", "vendor management",
        "team management", "inventory",
    ],
    "Finance and Sales": [
        "financial modeling", "forecasting", "budgeting", "variance analysis",
        "lead generation", "negotiation", "pipeline management",
    ],
    "Support and QA": [
        "customer service", "ticketing", "troubleshooting", "sla",
        "manual testing", "automation testing", "api testing",
        "bug reporting", "test cases",
    ],
    "Security and Infrastructure": [
        "network security", "siem", "incident response", "risk assessment",
        "firewalls", "ci/cd", "monitoring", "terraform", "networking",
        "backup", "performance tuning",
    ],
}

SKILL_ALIASES = {
    "react js": "react",
    "react.js": "react",
    "next js": "next.js",
    "nextjs": "next.js",
    "express js": "express",
    "express.js": "express",
    "node js": "nodejs",
    "node.js": "nodejs",
    "rest apis": "rest api",
    "api development": "api",
    "postgres": "postgresql",
}


def _normalize_skill(skill):
    normalized = re.sub(r"\s+", " ", skill.strip().lower())
    return SKILL_ALIASES.get(normalized, normalized)


def extract_skills(text):
    """Return a sorted list of detected skills from text."""
    normalized_text = text.lower()
    detected = set()

    for skills in SKILL_DICTIONARY.values():
        for skill in skills:
            pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9+#.])"
            if re.search(pattern, normalized_text):
                detected.add(_normalize_skill(skill))

    return sorted(detected)


def compare_skills(resume_skills, required_skills):
    """Calculate overlapping and missing skills for a candidate."""
    resume_set = {_normalize_skill(skill) for skill in resume_skills if skill}
    required_set = {_normalize_skill(skill) for skill in required_skills if skill}

    if not required_set:
        return sorted(resume_set), [], 0.0

    overlap = sorted(resume_set.intersection(required_set))
    missing = sorted(required_set.difference(resume_set))
    score = len(overlap) / len(required_set)
    return overlap, missing, score


def split_required_skills(text):
    """Support comma, newline, and semicolon separated recruiter skill input."""
    if not text:
        return []
    return [
        _normalize_skill(skill)
        for skill in re.split(r"[,;\n]+|\s+\band\b\s+", text)
        if skill.strip()
    ]
