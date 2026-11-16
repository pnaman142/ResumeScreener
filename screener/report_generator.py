"""
Report Generator for Candidate Screening and Ranking.
Produces CSV summaries, detailed JSON objects, and formatted Markdown reports.
"""

import csv
import io
import json
from typing import Any, Dict, List


def generate_ranking_dataframe(rankings: List[Dict[str, Any]]):
    """
    Generate a clean pandas DataFrame suitable for tabular display or CSV export.
    """
    import pandas as pd

    records = []
    for item in rankings:
        c = item["candidate"]
        records.append({
            "Rank": item.get("rank", 0),
            "Candidate Name": c.get("name", "Unknown"),
            "Match Score (%)": item.get("composite_score", 0.0),
            "Status": item.get("status", "N/A"),
            "TF-IDF Similarity (%)": item.get("tfidf_score", 0.0),
            "Skill Match (%)": item.get("skill_score", 0.0),
            "Experience (Yrs)": c.get("experience", {}).get("estimated_years", 0.0),
            "Education": ", ".join(c.get("education", {}).get("degrees", [])) or "Listed",
            "Matched Skills Count": item.get("matched_skills_count", 0),
            "Matched Skills": ", ".join(item.get("matched_skills", [])),
            "Missing Skills": ", ".join(item.get("missing_skills", [])),
            "Email": c.get("email", ""),
            "Phone": c.get("phone", ""),
            "File": c.get("filename", "")
        })

    return pd.DataFrame(records)


def export_rankings_csv(rankings: List[Dict[str, Any]]) -> str:
    """Export candidate rankings to CSV string."""
    df = generate_ranking_dataframe(rankings)
    return df.to_csv(index=False)


def generate_candidate_summary_markdown(evaluation: Dict[str, Any]) -> str:
    """
    Generate an individual comprehensive markdown summary report for a candidate.
    """
    cand = evaluation["candidate"]
    matched_skills = evaluation.get("matched_skills", [])
    missing_skills = evaluation.get("missing_skills", [])
    add_skills = evaluation.get("additional_skills", [])

    matched_str = ", ".join(f"`{s}`" for s in matched_skills) if matched_skills else "_None_"
    missing_str = ", ".join(f"`{s}`" for s in missing_skills) if missing_skills else "_None_"
    add_str = ", ".join(f"`{s}`" for s in add_skills[:10]) if add_skills else "_None_"

    report = f"""### Candidate Report: {cand.get('name', 'Candidate')}
- **Rank**: #{evaluation.get('rank', 'N/A')}
- **Overall Match Score**: **{evaluation.get('composite_score', 0)}%** ({evaluation.get('status', 'N/A')})
- **Contact**: Email: {cand.get('email', 'N/A')} | Phone: {cand.get('phone', 'N/A')}
- **File Source**: `{cand.get('filename', 'N/A')}`

#### Score Breakdown
- **TF-IDF Semantic Similarity**: {evaluation.get('tfidf_score', 0)}%
- **Skill Coverage**: {evaluation.get('skill_score', 0)}% ({evaluation.get('matched_skills_count', 0)}/{evaluation.get('total_required_skills', 0)} matched)
- **Experience Alignment**: {evaluation.get('exp_score', 0)}% (Estimated: {cand.get('experience', {}).get('estimated_years', 0)} years)
- **Education Alignment**: {evaluation.get('edu_score', 0)}%

#### Skill Assessment
- **Matched Skills**: {matched_str}
- **Missing Requirements**: {missing_str}
- **Additional Candidate Skills**: {add_str}

#### Experience & Background
{cand.get('experience', {}).get('summary', 'No detailed experience summary extracted.')}

#### Education Background
- Degrees: {', '.join(cand.get('education', {}).get('degrees', [])) or 'None detected'}
- Majors: {', '.join(cand.get('education', {}).get('majors', [])) or 'None detected'}
- Summary: {cand.get('education', {}).get('summary', 'Listed in resume')}
"""
    return report.strip()


def export_full_json_report(ranked_result: Dict[str, Any]) -> str:
    """Export complete screening result to pretty-printed JSON."""
    # Create JSON serializable copy
    exportable = {
        "metrics": ranked_result.get("metrics", {}),
        "job_requirements": {
            "skills": ranked_result.get("jd_requirements", {}).get("skills", []),
            "min_experience_years": ranked_result.get("jd_requirements", {}).get("min_experience_years", 0),
            "preferred_degrees": ranked_result.get("jd_requirements", {}).get("preferred_degrees", [])
        },
        "candidates": []
    }

    for item in ranked_result.get("rankings", []):
        cand = item["candidate"]
        exportable["candidates"].append({
            "rank": item.get("rank"),
            "name": cand.get("name"),
            "composite_score": item.get("composite_score"),
            "status": item.get("status"),
            "tfidf_score": item.get("tfidf_score"),
            "skill_score": item.get("skill_score"),
            "experience_years": cand.get("experience", {}).get("estimated_years"),
            "matched_skills": item.get("matched_skills"),
            "missing_skills": item.get("missing_skills"),
            "email": cand.get("email"),
            "phone": cand.get("phone"),
            "filename": cand.get("filename")
        })

    return json.dumps(exportable, indent=2)

