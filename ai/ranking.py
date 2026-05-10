"""Candidate ranking logic for ResumeIQ."""


def calculate_final_score(semantic_score, skill_score, experience_score, project_score):
    """Weighted scoring formula used to rank candidates."""
    final_score = (
        semantic_score * 0.40
        + skill_score * 0.35
        + experience_score * 0.15
        + project_score * 0.10
    )
    return round(final_score * 100, 2)


def rank_candidates(candidates):
    """Return candidates sorted by final score in descending order."""
    return sorted(candidates, key=lambda candidate: candidate["final_score"], reverse=True)
