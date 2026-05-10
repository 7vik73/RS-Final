"""Rule-based resume strength scoring."""


def calculate_resume_strength(raw_text, skills, sections):
    """Return a 0-10 resume quality score using explainable rules."""
    score = 0.0
    text_lower = raw_text.lower()

    if len(raw_text.split()) >= 200:
        score += 2.0
    elif len(raw_text.split()) >= 100:
        score += 1.0

    score += min(len(skills) / 10, 1.0) * 2.0

    if sections.get("experience"):
        score += 2.0
    if sections.get("projects"):
        score += 1.5
    if sections.get("education"):
        score += 1.0
    if sections.get("certifications") or "certification" in text_lower:
        score += 1.0
    if "@" in raw_text and any(char.isdigit() for char in raw_text):
        score += 0.5

    return round(min(score, 10.0), 1)
