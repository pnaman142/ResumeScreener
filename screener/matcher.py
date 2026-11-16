"""
Matching and Ranking Engine for AI Resume Screening.
Combines TF-IDF Cosine Similarity, Skill Set Overlap, Experience Relevance,
and Education Alignment into a robust composite score.
"""

import re
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from screener.extractor import (
    DEGREE_PATTERNS,
    extract_candidate_profile,
    extract_skills,
)
from screener.nlp_preprocessor import preprocess


def extract_jd_requirements(jd_text: str) -> Dict[str, Any]:
    """
    Extract required skills, target experience years, and degree preferences
    from a job description.
    """
    skills = extract_skills(jd_text)

    # Required experience detection (e.g., "5+ years", "3-5 years")
    exp_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\b", jd_text, flags=re.IGNORECASE)
    min_years = float(exp_match.group(1)) if exp_match else 0.0

    # Required education detection
    preferred_degrees = []
    for pattern in DEGREE_PATTERNS:
        match = re.search(pattern, jd_text, flags=re.IGNORECASE)
        if match:
            preferred_degrees.append(match.group(0).upper())

    return {
        "skills": skills,
        "min_experience_years": min_years,
        "preferred_degrees": list(set(preferred_degrees)),
        "raw_text": jd_text,
    }


def compute_tfidf_similarities(
    jd_text: str, candidate_texts: List[str]
) -> List[float]:
    """
    Compute Cosine Similarity between Job Description and candidate resumes
    using Scikit-learn TF-IDF Vectorizer with unigrams & bigrams.
    """
    if not candidate_texts:
        return []

    # Preprocess text corpus (tokenization, stop words, lemmatization)
    clean_jd = preprocess(jd_text)
    clean_candidates = [preprocess(t) for t in candidate_texts]

    corpus = [clean_jd] + clean_candidates
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=5000,
        stop_words="english",
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        jd_vector = tfidf_matrix[0:1]
        resume_vectors = tfidf_matrix[1:]

        # Compute cosine similarity
        similarities = cosine_similarity(jd_vector, resume_vectors).flatten()
        return [float(max(0.0, min(1.0, s))) for s in similarities]
    except Exception:
        # Fallback if corpus is nearly empty
        return [0.0] * len(candidate_texts)


def evaluate_candidate_fit(
    candidate: Dict[str, Any],
    jd_requirements: Dict[str, Any],
    tfidf_score: float,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Evaluate single candidate against job requirements using composite scoring.
    """
    if weights is None:
        weights = {
            "tfidf": 0.35,
            "skills": 0.45,
            "experience": 0.10,
            "education": 0.10,
        }

    # Normalize weights to sum to 1.0
    total_w = sum(weights.values()) or 1.0
    w_tfidf = weights.get("tfidf", 0.35) / total_w
    w_skills = weights.get("skills", 0.45) / total_w
    w_exp = weights.get("experience", 0.10) / total_w
    w_edu = weights.get("education", 0.10) / total_w

    # 1. Skill Match Calculation
    jd_skills = set(jd_requirements.get("skills", []))
    cand_skills = set(candidate.get("skills", []))

    matched_skills = sorted(list(jd_skills.intersection(cand_skills)))
    missing_skills = sorted(list(jd_skills - cand_skills))
    additional_skills = sorted(list(cand_skills - jd_skills))

    if jd_skills:
        skill_score = len(matched_skills) / len(jd_skills)
    else:
        skill_score = tfidf_score  # If JD lists no explicit skills, fallback to TF-IDF

    # 2. Experience Match Calculation
    req_exp = jd_requirements.get("min_experience_years", 0.0)
    cand_exp = candidate.get("experience", {}).get("estimated_years", 0.0)

    if req_exp <= 0.0:
        exp_score = 1.0
    else:
        if cand_exp >= req_exp:
            exp_score = 1.0
        else:
            exp_score = max(0.2, cand_exp / req_exp)

    # 3. Education Match Calculation
    preferred_degrees = jd_requirements.get("preferred_degrees", [])
    cand_degrees = candidate.get("education", {}).get("degrees", [])

    if not preferred_degrees:
        edu_score = 1.0
    else:
        has_match = any(
            any(p.lower() in d.lower() or d.lower() in p.lower() for d in cand_degrees)
            for p in preferred_degrees
        )
        edu_score = 1.0 if has_match else 0.5

    # Normalize TF-IDF cosine score (full document cosine similarity for technical texts
    # typically peaks around 0.35-0.45 for highly matching resumes vs job specs).
    tfidf_normalized = min(1.0, tfidf_score / 0.35) if tfidf_score > 0 else 0.0

    # 4. Composite Score (0.0 to 100.0)
    composite = (
        (w_tfidf * tfidf_normalized)
        + (w_skills * skill_score)
        + (w_exp * exp_score)
        + (w_edu * edu_score)
    ) * 100.0
    composite_score = round(max(0.0, min(100.0, composite)), 1)

    # Category Label
    if composite_score >= 75.0:
        status = "Strong Match"
        status_color = "#2E7D32"  # Deep green
    elif composite_score >= 60.0:
        status = "Good Match"
        status_color = "#D97706"  # Amber
    elif composite_score >= 45.0:
        status = "Moderate Match"
        status_color = "#E65100"  # Orange
    else:
        status = "Low Match"
        status_color = "#C62828"  # Red

    return {
        "candidate": candidate,
        "composite_score": composite_score,
        "status": status,
        "status_color": status_color,
        "tfidf_score": round(tfidf_score * 100.0, 1),
        "tfidf_normalized_score": round(tfidf_normalized * 100.0, 1),
        "skill_score": round(skill_score * 100.0, 1),
        "exp_score": round(exp_score * 100.0, 1),
        "edu_score": round(edu_score * 100.0, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "matched_skills_count": len(matched_skills),
        "total_required_skills": len(jd_skills),
    }


def rank_candidates(
    jd_text: str,
    candidates: List[Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Rank a list of parsed candidate profiles against a Job Description.
    Returns sorted rankings, summary metrics, and JD requirement metadata.
    """
    if not candidates:
        return {"rankings": [], "jd_requirements": {}, "metrics": {}}

    jd_reqs = extract_jd_requirements(jd_text)
    candidate_texts = [c.get("raw_text", "") for c in candidates]

    # Compute TF-IDF Cosine Similarities in batch
    tfidf_scores = compute_tfidf_similarities(jd_text, candidate_texts)

    evaluations = []
    for cand, tf_score in zip(candidates, tfidf_scores):
        ev = evaluate_candidate_fit(cand, jd_reqs, tf_score, weights)
        evaluations.append(ev)

    # Sort candidates descending by composite score, then skill score, then tfidf
    ranked = sorted(
        evaluations,
        key=lambda x: (x["composite_score"], x["skill_score"], x["tfidf_score"]),
        reverse=True,
    )

    # Assign 1-based ranks
    for idx, item in enumerate(ranked, start=1):
        item["rank"] = idx

    avg_score = (
        round(float(np.mean([r["composite_score"] for r in ranked])), 1)
        if ranked
        else 0.0
    )
    top_score = ranked[0]["composite_score"] if ranked else 0.0

    return {
        "rankings": ranked,
        "jd_requirements": jd_reqs,
        "metrics": {
            "total_candidates": len(ranked),
            "top_score": top_score,
            "average_score": avg_score,
            "strong_matches": sum(1 for r in ranked if r["status"] == "Strong Match"),
            "good_matches": sum(1 for r in ranked if r["status"] == "Good Match"),
        },
    }

