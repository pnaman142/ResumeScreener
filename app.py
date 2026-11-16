"""
TalentPulse AI Resume Screener & Candidate Ranking Application.
Expertly redesigned UI/UX with warm color palette, streamlined leaderboard,
and seamlessly integrated candidate deep-dive view.
"""

import os
import io
import pandas as pd
import streamlit as st
import altair as alt

from screener.parser import parse_resume, segment_sections
from screener.extractor import extract_candidate_profile, extract_skills
from screener.matcher import rank_candidates, extract_jd_requirements
from screener.report_generator import (
    generate_ranking_dataframe,
    export_rankings_csv,
    generate_candidate_summary_markdown,
    export_full_json_report,
)

# ----------------- Page Configuration -----------------
st.set_page_config(
    page_title="TalentPulse AI | Resume Screener & Ranker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- Warm Color Custom CSS -----------------
WARM_CSS = """
<style>
    /* Warm palette variables */
    :root {
        --primary-amber: #D97706;
        --primary-hover: #B45309;
        --warm-bg: #FAF8F5;
        --sidebar-bg: #F8F5F0;
        --card-bg: #FFFFFF;
        --border-color: #EEDCC9;
        --text-dark: #1F2937;
        --text-muted: #6B7280;
        --tag-match-bg: #DEF7EC;
        --tag-match-text: #03543F;
        --tag-missing-bg: #FEE2E2;
        --tag-missing-text: #991B1B;
        --tag-neutral-bg: #FEF3C7;
        --tag-neutral-text: #92400E;
    }

    /* Main container styling */
    .stApp {
        background-color: var(--warm-bg);
        color: var(--text-dark);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* 1. Main Content Area: Minimum clean space directly below the Deploy navbar */
    header[data-testid="stHeader"] {
        height: 2.75rem !important;
        background: transparent !important;
        z-index: 99 !important;
    }
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding-top: 3.25rem !important;
        padding-bottom: 2rem !important;
        margin-top: 0rem !important;
    }

    /* 2. Sidebar Container */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }

    /* Sidebar Header (collapse/toggle sidebar button area) */
    [data-testid="stSidebarHeader"] {
        height: 2.2rem !important;
        min-height: 2.2rem !important;
        max-height: 2.2rem !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        margin-bottom: 0rem !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        margin-top: 0rem !important;
    }

    /* Sidebar User Content: Strip top padding so heading aligns right below toggle */
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
        margin-top: -0.25rem !important;
    }
    [data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"],
    [data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] {
        padding-top: 0rem !important;
        gap: 0.65rem !important;
    }

    /* Sidebar Heading Title with minimal top margin */
    [data-testid="stSidebar"] h3:first-child,
    [data-testid="stSidebarUserContent"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #9A3412;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 0.15rem !important;
        padding-top: 0rem !important;
        margin-bottom: 0.4rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        padding: 8px 12px;
        border: 1px dashed #D97706;
        border-radius: 8px;
        background-color: #FFFFFF;
    }

    /* Header Banner with compact margins */
    .header-banner {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        border: 1px solid #FED7AA;
        border-radius: 12px;
        padding: 18px 24px;
        margin-top: 0rem !important;
        margin-bottom: 18px;
        box-shadow: 0 2px 4px rgba(217, 119, 6, 0.05);
    }
    .header-title {
        color: #9A3412;
        font-size: 2.0rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-subtitle {
        color: #7C2D12;
        font-size: 1.0rem;
        margin-bottom: 0;
    }

    /* Top Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        text-align: center;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(217, 119, 6, 0.08);
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #9A3412;
    }
    .metric-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #78716C;
        margin-top: 4px;
    }

    /* Tabs Styling & Vertical Spacing */
    .stTabs {
        margin-top: 24px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid var(--border-color);
        margin-bottom: 20px;
        padding-bottom: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 9px 20px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #78716C;
        border-radius: 8px 8px 0 0;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #D97706;
        background-color: #FFF7ED;
    }
    .stTabs [aria-selected="true"] {
        color: #9A3412 !important;
        border-bottom: 3px solid #D97706 !important;
        background-color: rgba(254, 243, 199, 0.35);
    }

    /* Deep-Dive Card */
    .deepdive-container {
        background-color: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 22px 26px;
        margin-top: 24px;
        margin-bottom: 24px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .deepdive-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        border-bottom: 1px solid #F3E8DC;
        padding-bottom: 14px;
        margin-bottom: 16px;
    }
    .deepdive-name {
        margin: 0;
        color: #9A3412;
        font-size: 1.55rem;
        font-weight: 700;
    }
    .deepdive-meta {
        margin: 4px 0 0 0;
        color: #6B7280;
        font-size: 0.9rem;
    }
    .deepdive-score-badge {
        text-align: right;
    }

    /* Mini metric card inside deep dive */
    .deepdive-mini-card {
        background-color: #FAF8F5;
        border: 1px solid #F3E8DC;
        border-radius: 8px;
        padding: 12px 14px;
        text-align: center;
    }
    .deepdive-mini-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #9A3412;
    }
    .deepdive-mini-label {
        font-size: 0.78rem;
        color: #78716C;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-top: 2px;
    }

    /* Badges */
    .badge-match {
        display: inline-block;
        background-color: var(--tag-match-bg);
        color: var(--tag-match-text);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 3px;
        border: 1px solid #BCF0DA;
    }
    .badge-missing {
        display: inline-block;
        background-color: var(--tag-missing-bg);
        color: var(--tag-missing-text);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 3px;
        border: 1px solid #FBD5D5;
    }
    .badge-neutral {
        display: inline-block;
        background-color: var(--tag-neutral-bg);
        color: var(--tag-neutral-text);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 3px;
        border: 1px solid #FDE68A;
    }

    /* Buttons Styling */
    button[data-testid="baseButton-primary"],
    button[kind="primary"] {
        background-color: #D97706 !important;
        color: #FFFFFF !important;
        border: 1px solid #B45309 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 4px rgba(217, 119, 6, 0.2) !important;
    }
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background-color: #B45309 !important;
        border-color: #9A3412 !important;
        color: #FFFFFF !important;
    }

    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border: 1px solid #EEDCC9 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #FFF7ED !important;
        color: #9A3412 !important;
        border-color: #D97706 !important;
    }

    /* Candidate button inside table column */
    div[data-testid="column"] button {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.90rem !important;
        height: auto !important;
        min-height: 38px !important;
    }

    /* Instruction Callout */
    .hint-callout {
        background-color: #FFFBEB;
        border-left: 4px solid #D97706;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 14px;
        font-size: 0.88rem;
        color: #92400E;
    }
</style>
"""
st.markdown(WARM_CSS, unsafe_allow_html=True)

# ----------------- Sample Data Paths -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JD_DIR = os.path.join(BASE_DIR, "data", "sample_job_descriptions")
RESUME_DIR = os.path.join(BASE_DIR, "data", "sample_resumes")

PRESET_JDS = {
    "Senior Machine Learning Engineer": "senior_ml_engineer.txt",
    "Full Stack Developer": "full_stack_developer.txt",
    "Data Analyst": "data_analyst.txt",
}


def load_preset_jd(filename: str) -> str:
    path = os.path.join(JD_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def load_preset_resumes():
    candidates = []
    if not os.path.exists(RESUME_DIR):
        return candidates

    files = [f for f in os.listdir(RESUME_DIR) if f.lower().endswith(".pdf")]
    # If no PDFs, fallback to TXT
    if not files:
        files = [f for f in os.listdir(RESUME_DIR) if f.lower().endswith(".txt")]

    for f in sorted(files):
        path = os.path.join(RESUME_DIR, f)
        try:
            raw_text = parse_resume(path)
            cand = extract_candidate_profile(raw_text, f)
            candidates.append(cand)
        except Exception as e:
            st.warning(f"Could not load {f}: {e}")
    return candidates


# ----------------- Sidebar -----------------
with st.sidebar:
    st.markdown("### ⚙️ Screening Configuration")

    # Target Job Description
    jd_choice = st.selectbox(
        "Select Job Description Preset or Custom",
        ["Select Preset..."] + list(PRESET_JDS.keys()) + ["Custom Input"],
        index=1,
    )

    default_jd_text = ""
    if jd_choice in PRESET_JDS:
        default_jd_text = load_preset_jd(PRESET_JDS[jd_choice])

    # Compact text area to eliminate sidebar crowding
    jd_input_text = st.text_area(
        "Job Description Text",
        value=default_jd_text,
        height=135,
        placeholder="Paste job description requirements, qualifications, and skills here...",
    )

    jd_file_upload = st.file_uploader(
        "Upload Job Description (.txt, .md, .pdf)",
        type=["txt", "md", "pdf"],
        key="jd_uploader",
    )
    if jd_file_upload is not None:
        try:
            jd_input_text = parse_resume(jd_file_upload, jd_file_upload.name)
            st.success(f"Loaded JD: {jd_file_upload.name}")
        except Exception as e:
            st.error(f"Error reading JD file: {e}")

    # Equal balanced spacing without divider lines or subheadings
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Candidate Resumes
    use_preset_resumes = st.checkbox(
        "Include Pre-loaded Samples (5 Candidates)",
        value=True,
        help="Loads sample candidates (ML Engineer, Frontend, Full Stack, Data Analyst, DevOps) in PDF format.",
    )

    uploaded_resumes = st.file_uploader(
        "Upload Custom Resumes",
        type=["pdf", "txt", "docx", "md"],
        accept_multiple_files=True,
    )

    # Equal balanced spacing
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Scoring Weights Tuning
    with st.expander("⚖️ Customize Scoring Weights", expanded=False):
        st.caption("Adjust weight contributions (must total 100%).")
        w_skills = st.slider("Skill Match Weight (%)", 10, 70, 45, 5)
        w_tfidf = st.slider("TF-IDF Semantic Similarity (%)", 10, 60, 35, 5)
        w_exp = st.slider("Experience Weight (%)", 0, 30, 10, 5)
        w_edu = st.slider("Education Weight (%)", 0, 30, 10, 5)

        total_weight = w_skills + w_tfidf + w_exp + w_edu
        if total_weight != 100:
            st.warning(f"Weights currently sum to {total_weight}% (normalized automatically).")

        weights = {
            "skills": w_skills / 100.0,
            "tfidf": w_tfidf / 100.0,
            "experience": w_exp / 100.0,
            "education": w_edu / 100.0,
        }


# ----------------- Main Interface Header -----------------
st.markdown(
    """
    <div class="header-banner">
        <div class="header-title">
            <span>📄</span>
            <span>TalentPulse AI Resume Screener</span>
        </div>
        <p class="header-subtitle">
            Automated resume parsing, NLP skill extraction, and TF-IDF semantic relevance ranking.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Verify inputs
if not jd_input_text.strip():
    st.info("👈 Please select or paste a Job Description in the sidebar to begin screening.")
    st.stop()

# Load all candidate profiles
candidates = []
if use_preset_resumes:
    candidates.extend(load_preset_resumes())

if uploaded_resumes:
    for f in uploaded_resumes:
        try:
            raw_text = parse_resume(f, f.name)
            cand = extract_candidate_profile(raw_text, f.name)
            candidates.append(cand)
        except Exception as e:
            st.error(f"Failed to parse uploaded resume {f.name}: {e}")

if not candidates:
    st.warning("⚠️ No resumes available. Please upload candidate resumes or check the pre-loaded samples box.")
    st.stop()

# ----------------- Execution & Ranking -----------------
with st.spinner("Analyzing candidate resumes, extracting skills, and computing match scores..."):
    results = rank_candidates(jd_input_text, candidates, weights=weights)
    rankings = results["rankings"]
    metrics = results["metrics"]
    jd_reqs = results["jd_requirements"]

# ----------------- Top Metrics Summary -----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_candidates']}</div>
            <div class="metric-label">Resumes Screened</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['top_score']}%</div>
            <div class="metric-label">Top Match Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['average_score']}%</div>
            <div class="metric-label">Average Match Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['strong_matches']}</div>
            <div class="metric-label">Strong Matches</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------- Simplified Navigation Tabs -----------------
# Removed separate "Candidate Deep-Dive" tab; now integrated directly into Leaderboard
tab1, tab2, tab3 = st.tabs([
    "🏆 Candidate Leaderboard",
    "📊 Comparative Analytics",
    "ℹ️ Scoring Methodology"
])

# ----------------- TAB 1: Streamlined Leaderboard & Integrated Deep-Dive -----------------
with tab1:
    st.markdown("### 🏆 Candidate Ranking Leaderboard")
    st.caption("Ranked by composite AI score combining skill coverage, semantic TF-IDF relevance, experience, and education.")

    # Safely resolve selected candidate index as a valid integer within [0, len(rankings)-1]
    raw_idx = st.session_state.get("selected_candidate_idx", 0)
    try:
        cand_idx = int(raw_idx)
    except (ValueError, TypeError):
        cand_idx = 0

    if cand_idx < 0 or cand_idx >= len(rankings):
        cand_idx = 0
    st.session_state.selected_candidate_idx = cand_idx
    active_idx = cand_idx

    # Export Controls
    st.markdown("<div style='margin-top: 6px; margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    exp_col1, exp_col2, hint_col = st.columns([1.4, 1.4, 3.2])
    with exp_col1:
        st.download_button(
            label="📥 Export Rankings CSV",
            data=export_rankings_csv(rankings),
            file_name="candidate_rankings.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp_col2:
        st.download_button(
            label="📥 Export Full JSON Report",
            data=export_full_json_report(results),
            file_name="screening_report.json",
            mime="application/json",
            use_container_width=True,
        )
    with hint_col:
        st.markdown(
            """
            <div style="background-color: #FFFBEB; border-left: 3px solid #D97706; padding: 7px 12px; border-radius: 0 6px 6px 0; font-size: 0.84rem; color: #92400E;">
                💡 <em>Click any candidate name below to view their detailed profile.</em>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # Leaderboard Table Header (No Tick column, No Email, No PDF/File)
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: 0.7fr 2.5fr 2.6fr 1.8fr 1.1fr 1.3fr; background-color: #FDF6EE; border: 1px solid #EEDCC9; border-radius: 8px; padding: 10px 14px; font-weight: 700; font-size: 0.80rem; color: #9A3412; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
            <div>Rank</div>
            <div>Candidate Name (Click to View)</div>
            <div>Match Score</div>
            <div>Status</div>
            <div>TF-IDF</div>
            <div>Skills Matched</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render each candidate row cleanly without ticks or clipping
    for idx, item in enumerate(rankings):
        cand = item["candidate"]
        is_selected = (idx == active_idx)
        score_val = item["composite_score"]

        row_bg = "#FFFBEB" if is_selected else "#FFFFFF"
        row_border = "#D97706" if is_selected else "#F3E8DC"

        st.markdown(
            f"""
            <div style="background-color: {row_bg}; border: 1px solid {row_border}; border-radius: 8px; padding: 6px 12px; margin-bottom: 6px;">
            """,
            unsafe_allow_html=True
        )
        c_rank, c_name, c_score, c_status, c_tfidf, c_skills = st.columns([0.7, 2.5, 2.6, 1.8, 1.1, 1.3])

        with c_rank:
            st.markdown(
                f"<div style='font-size: 1.0rem; font-weight: 700; color: #9A3412; padding-top: 7px;'>#{item['rank']}</div>",
                unsafe_allow_html=True
            )

        with c_name:
            if st.button(
                f"👤 {cand['name']}",
                key=f"cand_btn_{idx}_{jd_choice}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
                help=f"Click to inspect detailed profile for {cand['name']}"
            ):
                st.session_state.selected_candidate_idx = idx
                st.rerun()

        with c_score:
            st.progress(score_val / 100.0, text=f"{score_val:.1f}%")

        with c_status:
            # Dedicated width & nowrap badge prevents any status text clipping
            st.markdown(
                f"""
                <div style="padding-top: 6px;">
                    <span style="display: inline-block; background-color: {item['status_color']}18; color: {item['status_color']}; border: 1px solid {item['status_color']}40; padding: 3px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.80rem; white-space: nowrap;">
                        {item['status']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c_tfidf:
            st.markdown(
                f"<div style='padding-top: 7px; font-weight: 600; color: #4B5563; font-size: 0.92rem;'>{item['tfidf_score']:.1f}%</div>",
                unsafe_allow_html=True
            )

        with c_skills:
            st.markdown(
                f"<div style='padding-top: 7px; font-weight: 600; color: #1F2937; font-size: 0.92rem;'>{item['matched_skills_count']} / {item['total_required_skills']}</div>",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- Integrated Candidate Deep-Dive View -----------------
    active_idx = st.session_state.selected_candidate_idx
    selected_eval = rankings[active_idx]
    c_info = selected_eval["candidate"]

    st.markdown(
        f"""
        <div class="deepdive-container">
            <div class="deepdive-header">
                <div>
                    <h3 class="deepdive-name">👤 {c_info['name']}</h3>
                    <p class="deepdive-meta">
                        📧 {c_info.get('email') or 'N/A'} &nbsp;•&nbsp; 📞 {c_info.get('phone') or 'N/A'} &nbsp;•&nbsp; 📁 {c_info.get('filename')}
                    </p>
                </div>
                <div class="deepdive-score-badge">
                    <span style="font-size: 1.85rem; font-weight: 700; color: {selected_eval['status_color']};">{selected_eval['composite_score']}%</span><br>
                    <span style="background-color: {selected_eval['status_color']}18; color: {selected_eval['status_color']}; padding: 3px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.82rem; border: 1px solid {selected_eval['status_color']}30;">
                        {selected_eval['status']} (Rank #{selected_eval['rank']})
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4-Metric Grid for the selected candidate
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="deepdive-mini-card">
                <div class="deepdive-mini-value">{selected_eval['tfidf_score']}%</div>
                <div class="deepdive-mini-label">TF-IDF Similarity</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="deepdive-mini-card">
                <div class="deepdive-mini-value">{selected_eval['skill_score']}%</div>
                <div class="deepdive-mini-label">Skill Coverage</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="deepdive-mini-card">
                <div class="deepdive-mini-value">{selected_eval['exp_score']}%</div>
                <div class="deepdive-mini-label">Experience Match</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="deepdive-mini-card">
                <div class="deepdive-mini-value">{selected_eval['edu_score']}%</div>
                <div class="deepdive-mini-label">Education Match</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Skills Comparison Cards (Matched vs Missing)
    col_sk1, col_sk2 = st.columns(2)
    with col_sk1:
        st.markdown(f"#### ✅ Matched Skills ({len(selected_eval['matched_skills'])})")
        if selected_eval["matched_skills"]:
            m_html = " ".join([f'<span class="badge-match">✓ {s}</span>' for s in selected_eval["matched_skills"]])
            st.markdown(m_html, unsafe_allow_html=True)
        else:
            st.caption("No direct required skill matches found.")

    with col_sk2:
        st.markdown(f"#### ⚠️ Missing Required Skills ({len(selected_eval['missing_skills'])})")
        if selected_eval["missing_skills"]:
            mis_html = " ".join([f'<span class="badge-missing">✕ {s}</span>' for s in selected_eval["missing_skills"]])
            st.markdown(mis_html, unsafe_allow_html=True)
        else:
            st.success("All identified required skills are present in this resume!")

    # Additional Candidate Skills
    if selected_eval["additional_skills"]:
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 💡 Additional Relevant Candidate Skills")
        add_html = " ".join([f'<span class="badge-neutral">{s}</span>' for s in selected_eval["additional_skills"]])
        st.markdown(add_html, unsafe_allow_html=True)

    # Experience & Education Overview
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    col_det1, col_det2 = st.columns(2)
    with col_det1:
        st.markdown("#### 💼 Experience Overview")
        st.write(f"**Estimated Experience:** {c_info['experience']['estimated_years']} years")
        st.markdown(f"```text\n{c_info['experience']['summary']}\n```")

    with col_det2:
        st.markdown("#### 🎓 Education Overview")
        degrees_str = ", ".join(c_info["education"]["degrees"]) if c_info["education"]["degrees"] else "Not detected"
        majors_str = ", ".join(c_info["education"]["majors"]) if c_info["education"]["majors"] else "Not detected"
        st.write(f"**Degrees:** {degrees_str}")
        st.write(f"**Fields of Study:** {majors_str}")
        st.markdown(f"```text\n{c_info['education']['summary']}\n```")

    # Download Candidate Individual Report & Raw Text Expander
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    cand_md = generate_candidate_summary_markdown(selected_eval)
    dl_cand_col, _ = st.columns([2, 3])
    with dl_cand_col:
        st.download_button(
            label=f"📥 Download Summary Report for {c_info['name']}",
            data=cand_md,
            file_name=f"{c_info['name'].lower().replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with st.expander(f"📄 View Parsed Raw Resume Text ({c_info['name']})"):
        st.text(c_info["raw_text"])

# ----------------- TAB 2: Comparative Analytics -----------------
with tab2:
    st.markdown("### 📊 Comparative Candidate Breakdown")
    st.caption("Visualizing candidate fit, skill coverage, and experience distribution.")

    chart_data = []
    for item in rankings:
        c = item["candidate"]
        chart_data.append({
            "Candidate": c["name"],
            "Composite Score": item["composite_score"],
            "Skill Score": item["skill_score"],
            "TF-IDF Similarity": item["tfidf_score"],
            "Experience Years": c["experience"]["estimated_years"],
            "Skills Matched": item["matched_skills_count"],
        })
    df_chart = pd.DataFrame(chart_data)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### 🎯 Overall Match Score by Candidate")
        bar_chart = (
            alt.Chart(df_chart)
            .mark_bar(cornerRadius=6, color="#D97706")
            .encode(
                x=alt.X("Composite Score:Q", title="Match Score (%)", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Candidate:N", sort="-x", title="Candidate"),
                tooltip=["Candidate", "Composite Score", "Skill Score", "Skills Matched"],
            )
            .properties(height=300)
        )
        st.altair_chart(bar_chart, use_container_width=True)

    with col_chart2:
        st.markdown("#### 🧠 Matched Skills vs Experience")
        scatter_chart = (
            alt.Chart(df_chart)
            .mark_circle(size=180, color="#B45309")
            .encode(
                x=alt.X("Skills Matched:Q", title="Number of Skills Matched"),
                y=alt.Y("Experience Years:Q", title="Years of Experience"),
                tooltip=["Candidate", "Composite Score", "Skills Matched", "Experience Years"],
            )
            .properties(height=300)
        )
        st.altair_chart(scatter_chart, use_container_width=True)

    # Job Description Detected Skills
    st.markdown("---")
    st.markdown("#### 📋 Extracted Job Requirements")
    st.caption("Skills automatically identified from the job description:")
    jd_skills = jd_reqs.get("skills", [])
    if jd_skills:
        badges = " ".join([f'<span class="badge-neutral">{s}</span>' for s in jd_skills])
        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.write("No explicit skills detected in JD; standard semantic TF-IDF matching applied.")

# ----------------- TAB 3: Methodology -----------------
with tab3:
    st.markdown("### ℹ️ Scoring Algorithm & Architecture")
    st.markdown(
        r"""
        TalentPulse AI evaluates resumes through a multi-stage Natural Language Processing (NLP) pipeline:

        #### 1. Text Parsing & Section Segmentation
        - **Multi-Format Ingestion**: Supports `.pdf` (via `pdfplumber` and `pypdf`), `.docx` (via `python-docx`), and plain `.txt` files.
        - **Section Segmentation**: Employs boundary pattern matching to isolate `Skills`, `Work Experience`, and `Education` sections.

        #### 2. NLP Preprocessing
        - Normalizes Unicode and removes non-standard bullet characters and artifacts.
        - Special technical token protection prevents symbols such as `C++`, `C#`, and `.NET` from regex word-boundary degradation.
        - Stop words removal using NLTK English stopwords enriched with resume noise filters.
        - Lemmatization via WordNet Lemmatizer to reduce inflected forms down to root lemmas.

        #### 3. Matching & Scoring Components
        The final **Composite Relevance Score** \(S\) is computed as a weighted combination:
        $$S = (w_{\text{skills}} \cdot S_{\text{skills}} + w_{\text{tfidf}} \cdot S_{\text{tfidf}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{edu}} \cdot S_{\text{edu}}) \times 100$$

        | Component | Default Weight | Description |
        | :--- | :---: | :--- |
        | **Skill Set Overlap** | **45%** | Matches candidate skills against required skills extracted from the job description. |
        | **TF-IDF Semantic Similarity** | **35%** | Scikit-learn TF-IDF Vectorizer with unigrams & bigrams and Cosine Similarity, normalized for domain alignment. |
        | **Experience Alignment** | **10%** | Compares estimated candidate experience years against target job requirements. |
        | **Education Alignment** | **10%** | Evaluates degrees (BS, MS, PhD) and majors (Computer Science, Data Science, etc.). |

        #### 4. Candidate Qualification Categories
        - 🟢 **Strong Match (≥ 75%)**: Highly aligned across skills, domain keywords, and seniority.
        - 🟠 **Good Match (60% - 74%)**: Strong candidate with minor skill or experience gaps.
        - 🟧 **Moderate Match (45% - 59%)**: Partial overlap; may require cross-training.
        - 🔴 **Low Match (< 45%)**: Lacks core required technical competencies.
        """
    )
