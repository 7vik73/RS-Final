"""NLP preprocessing utilities powered by NLTK."""

import re
import string
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was",
    "were", "will", "with", "this", "or", "you", "your", "can", "using",
}

_NLTK_DOWNLOAD_CHECKED = False


def ensure_nltk_resources():
    """Download small NLTK resources only when they are missing."""
    global _NLTK_DOWNLOAD_CHECKED
    if _NLTK_DOWNLOAD_CHECKED:
        return
    if os.environ.get("HF_HUB_OFFLINE") == "1" or os.environ.get("TRANSFORMERS_OFFLINE") == "1":
        _NLTK_DOWNLOAD_CHECKED = True
        return
    if os.environ.get("RESUMEIQ_DOWNLOAD_NLTK") != "1":
        _NLTK_DOWNLOAD_CHECKED = True
        return

    resources = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
        "corpora/wordnet": "wordnet",
        "corpora/omw-1.4": "omw-1.4",
    }
    for path, package in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    nltk.download(package, quiet=True)
            except Exception:
                # Offline fallback is handled inside preprocess_text.
                pass
    _NLTK_DOWNLOAD_CHECKED = True


def preprocess_text(text):
    """Clean resume or job text for lightweight NLP comparison."""
    ensure_nltk_resources()
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))

    try:
        stop_words = set(stopwords.words("english"))
    except LookupError:
        stop_words = FALLBACK_STOPWORDS

    try:
        tokens = word_tokenize(text)
    except LookupError:
        tokens = re.findall(r"[a-zA-Z]+", text)

    lemmatizer = WordNetLemmatizer()

    def lemmatize(token):
        try:
            return lemmatizer.lemmatize(token)
        except LookupError:
            return token

    cleaned_tokens = [
        lemmatize(token)
        for token in tokens
        if token.isalpha() and token not in stop_words
    ]
    return " ".join(cleaned_tokens)
