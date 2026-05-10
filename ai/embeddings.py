"""Sentence Transformer embedding module.

The all-MiniLM-L6-v2 model is loaded lazily so the Flask app can start before
the first analysis request needs semantic AI.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    """Load the lightweight local semantic model once per Python process."""
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text):
    """Convert text into a semantic vector."""
    model = get_model()
    embedding = model.encode([text or ""], convert_to_numpy=True)[0]
    return np.asarray(embedding, dtype=float)
