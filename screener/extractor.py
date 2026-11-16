"""
Information Extraction module for Resumes and Job Descriptions.
Extracts Candidate Name, Contact Info, Skills, Education, and Experience.
"""

import re
from typing import Any, Dict, List, Set, Tuple

from screener.nlp_preprocessor import clean_text
from screener.parser import segment_sections
from screener.skills_taxonomy import (
    ALL_SKILL_KEYWORDS,
    get_canonical_skill,
    get_skill_category,
)

# Common degrees & academic keywords
DEGREE_PATTERNS = [
    r"\b(?:ph\.?d|doctor of philosophy)\b",
    r"\b(?:m\.?s\.?|master of science|master\'s|masters)\b",
    r"\b(?:m\.?tech|m\.?e\.?)\b",
    r"\b(?:b\.?s\.?|bachelor of science|bachelor\'s|bachelors)\b",
    r"\b(?:b\.?tech|b\.?e\.?)\b",
    r"\b(?:b\.?a\.?|bachelor of arts)\b",
    r"\b(?:m\.?b\.?a|master of business administration)\b",
    r"\b(?:associate degree|diploma)\b",
]

MAJOR_PATTERNS = [
    r"\bcomputer science\b",
    r"\bsoftware engineering\b",
    r"\bdata science\b",
    r"\binformation technology\b",
    r"\belectrical engineering\b",
    r"\bartificial intelligence\b",
    r"\bmathematics\b",
    r"\bstatistics\b",
    r"\bphysics\b",
    r"\bmechanical engineering\b",
    r"\bbusiness administration\b",
]


def extract_email(text: str) -> str:
    """Extract first valid email address from text."""
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_phone(text: str) -> str:
    """Extract standard telephone number format."""
    pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_name(text: str, filename: str = "") -> str:
    """
    Extract candidate name from header of resume.
    Falls back to cleaned filename if text pattern is inconclusive.
    """
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n") if line.strip()]
    ignore_words = {
        "resume", "curriculum", "vitae", "cv", "profile", "contact",
        "summary", "developer", "engineer", "scientist", "analyst", "page"
    }

    # Inspect the first 5 non-empty lines
    for line in lines[:5]:
        # Filter out lines with emails, links, or phone numbers
        if "@" in line or "http" in line or "www." in line:
            continue
        cleaned = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4:
            # Check that words are capitalized and not generic words
            if all(w.istitle() or w.isupper() for w in words):
                if not any(w.lower() in ignore_words for w in words):
                    return cleaned

    # Fallback to filename
    if filename:
        clean_fn = re.sub(r"(?i)(?:resume|cv|[_\-\d]|\.pdf|\.docx|\.txt)", " ", filename)
        clean_fn = re.sub(r"\s+", " ", clean_fn).strip()
        words = clean_fn.split()
        if words:
            return " ".join(words).title()

    return "Candidate"


def extract_skills(text: str) -> List[str]:
    """
    Extract technical and domain skills using boundary-safe regex matching
    against the taxonomy, returning deduplicated canonical names.
    """
    found_skills: Set[str] = set()
    cleaned = clean_text(text)
    text_lower = cleaned.lower()

    # Pre-sort keywords by length descending so multi-word skills match first
    sorted_keywords = sorted(ALL_SKILL_KEYWORDS, key=lambda k: len(k), reverse=True)

    for skill_kw in sorted_keywords:
        # Special handling for tricky symbols: c++, c#, .net
        if skill_kw in {"c++", "cpp"}:
            pattern = r"(?:\b|\s)c\+\+(?:\b|\s|,|;|\.|\))"
            if re.search(pattern, text_lower):
                found_skills.add(get_canonical_skill(skill_kw))
        elif skill_kw in {"c#", "csharp"}:
            pattern = r"(?:\b|\s)c\#(?:\b|\s|,|;|\.|\))"
            if re.search(pattern, text_lower):
                found_skills.add(get_canonical_skill(skill_kw))
        elif skill_kw in {".net", "dotnet"}:
            pattern = r"(?:\b|\s)\.net(?:\b|\s|,|;|\.|\))"
            if re.search(pattern, text_lower):
                found_skills.add(get_canonical_skill(skill_kw))
        elif len(skill_kw) <= 2:
            # Strict word boundary for short tokens like 'r', 'c', 'go', 'ui'
            pattern = rf"(?:\b){re.escape(skill_kw)}(?:\b)"
            if re.search(pattern, text_lower):
                found_skills.add(get_canonical_skill(skill_kw))
        else:
            # Standard word boundary
            pattern = rf"(?:\b){re.escape(skill_kw)}(?:\b)"
            if re.search(pattern, text_lower):
                found_skills.add(get_canonical_skill(skill_kw))

    return sorted(list(found_skills))


def extract_education(sections: Dict[str, str], full_text: str) -> Dict[str, Any]:
    """
    Extract educational qualifications, degrees, majors, and institutions.
    """
    edu_text = sections.get("education", "") or full_text
    found_degrees = []
    found_majors = []

    for pattern in DEGREE_PATTERNS:
        match = re.search(pattern, edu_text, flags=re.IGNORECASE)
        if match:
            found_degrees.append(match.group(0).upper())

    for pattern in MAJOR_PATTERNS:
        match = re.search(pattern, edu_text, flags=re.IGNORECASE)
        if match:
            found_majors.append(match.group(0).title())

    # Find graduation years
    year_pattern = r"\b(?:19|20)\d{2}\b"
    years = re.findall(year_pattern, edu_text)
    grad_year = max(years) if years else None

    # Education summary snippet
    edu_lines = [l.strip() for l in edu_text.split("\n") if l.strip()][:3]
    summary_snippet = " | ".join(edu_lines) if edu_lines else "Education details listed"

    return {
        "degrees": list(set(found_degrees)),
        "majors": list(set(found_majors)),
        "grad_year": grad_year,
        "summary": summary_snippet
    }


def extract_experience(sections: Dict[str, str], full_text: str) -> Dict[str, Any]:
    """
    Extract work experience details and estimate total years of experience.
    """
    exp_text = sections.get("experience", "") or full_text

    # 1. Search for explicit experience mentions (e.g. "5+ years of experience")
    explicit_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\b(?:\s*of\s*experience)?", full_text, flags=re.IGNORECASE)
    estimated_years = float(explicit_match.group(1)) if explicit_match else 0.0

    # 2. Extract year spans (e.g. 2018 - 2023 or 2020 - Present)
    date_range_pattern = r"\b(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|present|current)\b"
    matches = re.findall(date_range_pattern, exp_text, flags=re.IGNORECASE)
    span_years = 0.0

    current_year = 2026
    for start_yr, end_yr in matches:
        s = int(start_yr)
        e = current_year if end_yr.lower() in {"present", "current"} else int(end_yr)
        diff = max(0, e - s)
        span_years += diff

    # Choose reasonable max estimate
    total_years = max(estimated_years, min(span_years, 30.0))

    # Experience highlights (first 3-4 bullet lines)
    exp_lines = [l.strip() for l in exp_text.split("\n") if len(l.strip()) > 20][:4]
    summary = "\n".join(exp_lines) if exp_lines else "Experience details listed"

    return {
        "estimated_years": round(total_years, 1),
        "summary": summary
    }


def extract_candidate_profile(raw_text: str, filename: str = "") -> Dict[str, Any]:
    """
    Consolidated extraction for a candidate resume.
    """
    sections = segment_sections(raw_text)
    name = extract_name(raw_text, filename)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    skills = extract_skills(raw_text)
    education = extract_education(sections, raw_text)
    experience = extract_experience(sections, raw_text)

    # Group skills by domain category
    categorized_skills = {}
    for skill in skills:
        cat = get_skill_category(skill)
        categorized_skills.setdefault(cat, []).append(skill)

    return {
        "filename": filename,
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "categorized_skills": categorized_skills,
        "education": education,
        "experience": experience,
        "sections": sections,
        "raw_text": raw_text
    }

