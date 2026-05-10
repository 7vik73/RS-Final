"""Standalone Sentence Transformer semantic test for ResumeIQ.

This script demonstrates the core AI behavior without Flask, SQLite, or any
training step.

Run:
    python semantic_test.py
"""

from ai.matcher import semantic_similarity


def show_similarity(label, text_a, text_b):
    score = semantic_similarity(text_a, text_b)
    print(f"{label}: {score:.3f} ({score * 100:.2f}%)")
    print(f"  A: {text_a}")
    print(f"  B: {text_b}")
    print()


if __name__ == "__main__":
    show_similarity(
        "Expected high similarity",
        "Built REST APIs using FastAPI",
        "Backend API development",
    )
    show_similarity(
        "Expected low similarity",
        "Built REST APIs using FastAPI",
        "Graphic design using Photoshop",
    )
