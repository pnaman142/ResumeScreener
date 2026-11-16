"""
Unit and integration tests for AI Resume Screener.
Tests PDF parsing, TXT parsing, section extraction, skill extraction,
TF-IDF cosine similarity, ranking logic, and report generation.
"""

import os
import unittest

from screener.parser import parse_resume, segment_sections
from screener.nlp_preprocessor import preprocess, clean_text, tokenize
from screener.extractor import (
    extract_candidate_profile,
    extract_skills,
    extract_email,
    extract_phone,
)
from screener.matcher import rank_candidates, extract_jd_requirements
from screener.report_generator import (
    generate_ranking_dataframe,
    export_rankings_csv,
    generate_candidate_summary_markdown,
    export_full_json_report,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME_DIR = os.path.join(BASE_DIR, "data", "sample_resumes")
JD_DIR = os.path.join(BASE_DIR, "data", "sample_job_descriptions")


class TestResumeParser(unittest.TestCase):
    def test_parse_txt_resume(self):
        txt_path = os.path.join(RESUME_DIR, "alice_walker_senior_ml.txt")
        text = parse_resume(txt_path)
        self.assertIn("Alice Walker", text)
        self.assertIn("PyTorch", text)
        self.assertIn("Machine Learning", text)

    def test_parse_pdf_resume(self):
        pdf_path = os.path.join(RESUME_DIR, "alice_walker_senior_ml.pdf")
        text = parse_resume(pdf_path)
        self.assertTrue(len(text) > 100)
        self.assertIn("Alice Walker", text)
        self.assertIn("PyTorch", text)

    def test_segment_sections(self):
        txt_path = os.path.join(RESUME_DIR, "alice_walker_senior_ml.txt")
        text = parse_resume(txt_path)
        sections = segment_sections(text)
        self.assertTrue("skills" in sections)
        self.assertTrue("experience" in sections)
        self.assertTrue("education" in sections)


class TestNLPAndExtractor(unittest.TestCase):
    def test_preprocess(self):
        text = "Senior Software Engineer with C++ and Python developing deep learning models!"
        processed = preprocess(text)
        self.assertIn("python", processed)
        self.assertIn("c++", processed)
        self.assertNotIn("with", processed)  # Stop word removed

    def test_extract_skills(self):
        text = "Proficient in Python, C++, React, Docker, Kubernetes, and PostgreSQL."
        skills = extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("C++", skills)
        self.assertIn("React", skills)
        self.assertIn("Docker", skills)
        self.assertIn("Kubernetes", skills)
        self.assertIn("PostgreSQL", skills)

    def test_extract_candidate_profile(self):
        txt_path = os.path.join(RESUME_DIR, "bob_martinez_frontend_react.txt")
        raw_text = parse_resume(txt_path)
        profile = extract_candidate_profile(raw_text, "bob_martinez_frontend_react.txt")

        self.assertEqual(profile["name"], "Bob Martinez")
        self.assertEqual(profile["email"], "bob.martinez@email.com")
        self.assertIn("React", profile["skills"])
        self.assertIn("TypeScript", profile["skills"])
        self.assertGreater(profile["experience"]["estimated_years"], 0)


class TestMatcherAndRanking(unittest.TestCase):
    def setUp(self):
        # Load sample resumes
        resume_files = [
            "alice_walker_senior_ml.pdf",
            "bob_martinez_frontend_react.pdf",
            "charlie_patel_fullstack.pdf",
            "diana_chen_data_analyst.pdf",
            "evan_ross_junior_devops.pdf"
        ]
        self.candidates = []
        for fn in resume_files:
            path = os.path.join(RESUME_DIR, fn)
            raw_text = parse_resume(path)
            cand = extract_candidate_profile(raw_text, fn)
            self.candidates.append(cand)

    def test_rank_ml_role(self):
        jd_path = os.path.join(JD_DIR, "senior_ml_engineer.txt")
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        result = rank_candidates(jd_text, self.candidates)
        rankings = result["rankings"]

        # Alice Walker (ML Senior) must rank #1 for Senior ML role
        self.assertEqual(rankings[0]["candidate"]["name"], "Alice Walker")
        self.assertEqual(rankings[0]["status"], "Strong Match")
        self.assertGreaterEqual(rankings[0]["composite_score"], 70.0)

        # Diana or Bob or Evan should have lower scores
        self.assertGreater(rankings[0]["composite_score"], rankings[-1]["composite_score"])

    def test_rank_frontend_role(self):
        jd_path = os.path.join(JD_DIR, "full_stack_developer.txt")
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        result = rank_candidates(jd_text, self.candidates)
        top_candidates = [r["candidate"]["name"] for r in result["rankings"][:2]]
        # Charlie Patel or Bob Martinez should be top 2
        self.assertTrue("Charlie Patel" in top_candidates or "Bob Martinez" in top_candidates)

    def test_rank_data_analyst_role(self):
        jd_path = os.path.join(JD_DIR, "data_analyst.txt")
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        result = rank_candidates(jd_text, self.candidates)
        # Diana Chen must rank #1 for Data Analyst role
        self.assertEqual(result["rankings"][0]["candidate"]["name"], "Diana Chen")


class TestReports(unittest.TestCase):
    def test_reports_generation(self):
        jd_path = os.path.join(JD_DIR, "senior_ml_engineer.txt")
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        res_path = os.path.join(RESUME_DIR, "alice_walker_senior_ml.pdf")
        cand = extract_candidate_profile(parse_resume(res_path), "alice_walker_senior_ml.pdf")
        result = rank_candidates(jd_text, [cand])

        # Test CSV export
        csv_str = export_rankings_csv(result["rankings"])
        self.assertIn("Alice Walker", csv_str)
        self.assertIn("Match Score (%)", csv_str)

        # Test JSON export
        json_str = export_full_json_report(result)
        self.assertIn("Alice Walker", json_str)

        # Test Markdown summary
        md_str = generate_candidate_summary_markdown(result["rankings"][0])
        self.assertIn("Candidate Report: Alice Walker", md_str)


if __name__ == "__main__":
    unittest.main()

