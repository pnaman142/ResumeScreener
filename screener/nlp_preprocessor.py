"""
NLP Preprocessing module for text normalization, tokenization,
stop word removal, and lemmatization.
"""

import re
import unicodedata
from typing import List, Set

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Initialize lemmatizer and stop words
try:
    _STOP_WORDS: Set[str] = set(stopwords.words("english"))
except Exception:
    _STOP_WORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
        "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
        "what", "which", "who", "whom", "this", "that", "these", "those", "am",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but",
        "if", "or", "because", "as", "until", "while", "of", "at", "by", "for",
        "with", "about", "against", "between", "into", "through", "during", "before",
        "after", "above", "below", "to", "from", "up", "down", "in", "out", "on",
        "off", "over", "under", "again", "further", "then", "once", "here", "there",
        "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should",
        "now"
    }

RESUME_BOILERPLATE_WORDS = {
    "resume", "curriculum", "vitae", "cv", "page", "phone", "email", "address",
    "references", "available", "upon", "request", "date", "birth", "gender"
}
TOTAL_STOP_WORDS = _STOP_WORDS.union(RESUME_BOILERPLATE_WORDS)

try:
    _LEMMATIZER = WordNetLemmatizer()
except Exception:
    _LEMMATIZER = None


def clean_text(text: str) -> str:
    """Normalize unicode, whitespace, and remove noisy non-standard symbols."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    # Strip CID artifacts
    text = re.sub(r"\(cid:\d+\)", " ", text)
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u00B7\u25AA\u25CF]", " ", text)
    text = re.sub(r"[\u2013\u2014]", "-", text)
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201C\u201D]", '"', text)
    # Strip URL addresses
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def preserve_special_tech_tokens(text: str) -> str:
    """Protect tech words like C++, C#, .NET from regex word-boundary split."""
    # Convert C++ -> cpptoken, C# -> csharptoken, .NET -> dotnettoken
    text = re.sub(r"(?:\b|\s)C\+\+(?:\b|\s|,|;|\.|\)|$)", " cpptoken ", text, flags=re.IGNORECASE)
    text = re.sub(r"(?:\b|\s)C\#(?:\b|\s|,|;|\.|\)|$)", " csharptoken ", text, flags=re.IGNORECASE)
    text = re.sub(r"(?:\b|\s)\.NET(?:\b|\s|,|;|\.|\)|$)", " dotnettoken ", text, flags=re.IGNORECASE)
    return text


def restore_special_tech_tokens(token: str) -> str:
    """Restore mapped tokens back to readable tech names."""
    mapping = {
        "cpptoken": "c++",
        "csharptoken": "c#",
        "dotnettoken": ".net"
    }
    return mapping.get(token.lower(), token)


def tokenize(text: str) -> List[str]:
    """Tokenize text into words with punctuation stripped while preserving tokens."""
    cleaned = clean_text(text)
    protected = preserve_special_tech_tokens(cleaned)
    try:
        raw_tokens = word_tokenize(protected)
    except Exception:
        raw_tokens = re.findall(r"[A-Za-z0-9_\+\#\.]+", protected)

    res = []
    for t in raw_tokens:
        t_clean = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", t)
        if t_clean:
            res.append(restore_special_tech_tokens(t_clean.lower()))
    return res


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Filter out stop words and short symbols, while retaining key tech acronyms."""
    whitelist = {"r", "c", "go", "ai", "ml", "ui", "ux", "ci", "cd", "qa", "c++", "c#"}
    filtered = []
    for token in tokens:
        low = token.lower()
        if (low in whitelist or len(low) > 1) and (low not in TOTAL_STOP_WORDS):
            filtered.append(low)
    return filtered


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """Lemmatize tokens to base form using WordNetLemmatizer."""
    if not _LEMMATIZER:
        return tokens
    lemmatized = []
    for token in tokens:
        if token in {"c++", "c#", ".net", "r", "c", "go", "sql", "aws", "gcp"}:
            lemmatized.append(token)
        else:
            try:
                lem = _LEMMATIZER.lemmatize(token)
                lemmatized.append(lem)
            except Exception:
                lemmatized.append(token)
    return lemmatized


def preprocess(text: str, return_as_string: bool = True):
    """Full preprocessing pipeline: clean -> tokenize -> remove stopwords -> lemmatize."""
    tokens = tokenize(text)
    filtered = remove_stopwords(tokens)
    lemmatized = lemmatize_tokens(filtered)
    if return_as_string:
        return " ".join(lemmatized)
    return lemmatized
