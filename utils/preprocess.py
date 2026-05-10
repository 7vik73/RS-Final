"""NLP preprocessing utilities powered by NLTK."""

import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def ensure_nltk_resources():
    """Download small NLTK resources only when they are missing."""
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
            nltk.download(package, quiet=True)


def preprocess_text(text):
    """Clean resume or job text for lightweight NLP comparison."""
    ensure_nltk_resources()
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))

    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(text)
    cleaned_tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token.isalpha() and token not in stop_words
    ]
    return " ".join(cleaned_tokens)
