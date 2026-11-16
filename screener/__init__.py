"""
AI Resume Screener Package.
Core modules for resume parsing, NLP preprocessing, skill extraction,
TF-IDF cosine similarity matching, and candidate ranking.
"""

from screener.parser import parse_resume, segment_sections
from screener.nlp_preprocessor import preprocess, clean_text, tokenize
from screener.extractor import extract_candidate_profile, extract_skills
from screener.matcher import rank_candidates, extract_jd_requirements
from screener.report_generator import (
    generate_ranking_dataframe,
    export_rankings_csv,
    generate_candidate_summary_markdown,
    export_full_json_report,
)

__version__ = "1.0.0"

__all__ = [
    "parse_resume",
    "segment_sections",
    "preprocess",
    "clean_text",
    "tokenize",
    "extract_candidate_profile",
    "extract_skills",
    "rank_candidates",
    "extract_jd_requirements",
    "generate_ranking_dataframe",
    "export_rankings_csv",
    "generate_candidate_summary_markdown",
    "export_full_json_report",
]

