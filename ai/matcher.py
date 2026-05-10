"""Semantic matching using embeddings and cosine similarity."""

import numpy as np

from ai.embeddings import generate_embedding


def cosine_similarity(vector_a, vector_b):
    """Return cosine similarity between two vectors as a 0-1 value."""
    denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denominator == 0:
        return 0.0
    similarity = float(np.dot(vector_a, vector_b) / denominator)
    return max(0.0, min(1.0, similarity))


def semantic_similarity(text_a, text_b):
    """Generate embeddings dynamically and compare them."""
    embedding_a = generate_embedding(text_a)
    embedding_b = generate_embedding(text_b)
    return cosine_similarity(embedding_a, embedding_b)


def calculate_relevance_scores(resume_text, job_description, sections):
    """Calculate overall, project, and experience semantic relevance."""
    semantic_score = semantic_similarity(resume_text, job_description)
    project_score = semantic_similarity(sections.get("projects", ""), job_description)
    experience_score = semantic_similarity(sections.get("experience", ""), job_description)

    return {
        "semantic_score": semantic_score,
        "project_score": project_score,
        "experience_score": experience_score,
    }
