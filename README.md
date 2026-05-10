# ResumeIQ

ResumeIQ is a lightweight semantic AI resume screening and candidate ranking
system for recruiters. It uses Flask, SQLite, NLTK, Sentence Transformers,
`all-MiniLM-L6-v2`, cosine similarity, `pdfplumber`, `python-docx`,
TailwindCSS, and Chart.js.

## What It Does

- Recruiter/admin registration and login
- Job requirement creation
- Multiple PDF/DOCX resume uploads
- Resume parsing and contact extraction
- NLTK preprocessing
- Keyword and regex skill extraction
- Sentence Transformer embeddings
- Cosine similarity matching
- Weighted candidate ranking
- Shortlist and reject actions
- Analytics generated only from uploaded resumes

## Local Setup

```bash
cd resumeiq
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5001`.

## NLTK Resources

The app downloads small NLTK resources automatically when preprocessing first
runs:

- `punkt`
- `punkt_tab`
- `stopwords`
- `wordnet`
- `omw-1.4`

## Semantic Test

```bash
cd resumeiq
source venv/bin/activate
python semantic_test.py
```

The first pair should produce a higher similarity score than the unrelated
graphic design example.

## No Training Pipeline

ResumeIQ does not train a classifier, does not use TF-IDF training, and does
not require datasets. Embeddings are generated dynamically during resume
analysis with `all-MiniLM-L6-v2`, then compared using cosine similarity.
