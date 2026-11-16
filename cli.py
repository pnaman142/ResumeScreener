"""
Command-Line Interface (CLI) for AI Resume Screener.
Allows batch screening of PDF, TXT, and DOCX resumes against a Job Description.
"""

import argparse
import os
import sys
from typing import List

from screener.parser import parse_resume
from screener.extractor import extract_candidate_profile
from screener.matcher import rank_candidates
from screener.report_generator import (
    generate_ranking_dataframe,
    export_rankings_csv,
    generate_candidate_summary_markdown,
    export_full_json_report,
)


def load_resumes_from_sources(sources: List[str]):
    candidates = []
    for src in sources:
        if os.path.isdir(src):
            files = [
                os.path.join(src, f)
                for f in os.listdir(src)
                if f.lower().endswith((".pdf", ".txt", ".docx", ".md"))
            ]
            for fpath in files:
                try:
                    text = parse_resume(fpath)
                    fname = os.path.basename(fpath)
                    cand = extract_candidate_profile(text, fname)
                    candidates.append(cand)
                except Exception as e:
                    print(f"Warning: Failed to parse {fpath}: {e}", file=sys.stderr)
        elif os.path.isfile(src):
            try:
                text = parse_resume(src)
                fname = os.path.basename(src)
                cand = extract_candidate_profile(text, fname)
                candidates.append(cand)
            except Exception as e:
                print(f"Warning: Failed to parse {src}: {e}", file=sys.stderr)
        else:
            print(f"Warning: Path not found: {src}", file=sys.stderr)
    return candidates


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Screener & Candidate Ranker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--jd",
        required=True,
        help="Path to job description text file",
    )
    parser.add_argument(
        "--resumes",
        nargs="+",
        required=True,
        help="Path to one or more resume files (PDF/TXT/DOCX) or directories",
    )
    parser.add_argument(
        "--csv-output",
        default="ranking_report.csv",
        help="Output CSV file path (default: ranking_report.csv)",
    )
    parser.add_argument(
        "--json-output",
        default="",
        help="Optional output JSON file path",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed candidate summaries to stdout",
    )

    args = parser.parse_args()

    # 1. Read JD
    if not os.path.exists(args.jd):
        print(f"Error: Job description file '{args.jd}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(args.jd, "r", encoding="utf-8", errors="replace") as f:
        jd_text = f.read().strip()

    # 2. Parse Resumes
    print(f"\n==================================================")
    print(f"           AI RESUME SCREENER CLI                 ")
    print(f"==================================================")
    print(f"Loading Job Description: {args.jd}")
    print(f"Scanning Resumes from: {args.resumes}")

    candidates = load_resumes_from_sources(args.resumes)
    if not candidates:
        print("Error: No valid resumes could be loaded.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully parsed {len(candidates)} resumes.")
    print("Computing TF-IDF cosine similarities & evaluating skill match...\n")

    # 3. Match & Rank
    result = rank_candidates(jd_text, candidates)
    rankings = result["rankings"]
    metrics = result["metrics"]

    # 4. Display ASCII Leaderboard
    header = f"{'Rank':<5} | {'Candidate Name':<22} | {'Score':<7} | {'Status':<14} | {'Skills Matched':<14} | {'Exp':<5} | {'Source File'}"
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)

    for item in rankings:
        cand = item["candidate"]
        matched_ratio = f"{item['matched_skills_count']}/{item['total_required_skills']}"
        print(
            f"#{item['rank']:<4} | "
            f"{cand['name'][:22]:<22} | "
            f"{item['composite_score']:>5.1f}% | "
            f"{item['status']:<14} | "
            f"{matched_ratio:<14} | "
            f"{cand['experience']['estimated_years']:>4.1f}y | "
            f"{cand['filename']}"
        )
    print(separator)

    print(f"\nScreening Summary:")
    print(f"  Total Candidates: {metrics['total_candidates']}")
    print(f"  Top Match Score:  {metrics['top_score']}%")
    print(f"  Average Score:    {metrics['average_score']}%")
    print(f"  Strong Matches:   {metrics['strong_matches']}")
    print(f"  Good Matches:     {metrics['good_matches']}")

    # 5. Export CSV
    if args.csv_output:
        csv_data = export_rankings_csv(rankings)
        with open(args.csv_output, "w", encoding="utf-8") as f:
            f.write(csv_data)
        print(f"\nSaved CSV ranking report to: {args.csv_output}")

    # 6. Export JSON
    if args.json_output:
        json_data = export_full_json_report(result)
        with open(args.json_output, "w", encoding="utf-8") as f:
            f.write(json_data)
        print(f"Saved JSON ranking report to: {args.json_output}")

    # 7. Verbose reports
    if args.verbose:
        print("\n" + "=" * 50)
        print("INDIVIDUAL CANDIDATE DETAILED REPORTS")
        print("=" * 50)
        for item in rankings:
            print(generate_candidate_summary_markdown(item))
            print("-" * 50)


if __name__ == "__main__":
    main()

