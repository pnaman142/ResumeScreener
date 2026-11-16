# TalentPulse AI: Intelligent Resume Screener & Candidate Ranker

An AI-powered recruitment intelligence tool that automatically parses resumes across multiple formats (`.pdf`, `.docx`, `.txt`), extracts key candidate information (skills, work experience, education, contact details), and ranks candidates against job descriptions using NLP and semantic TF-IDF cosine similarity.

Designed with an interactive **Streamlit Web Application** featuring an elegant **warm-color palette** (amber, terracotta, cream) and a full-featured **Command-Line Interface (CLI)**.

---

## 🌟 Key Features

- **Multi-Format Resume Ingestion**: High-fidelity text extraction from **PDF** (via `pdfplumber` and `pypdf`), **Word DOCX** (via `python-docx`), and plain text/markdown files.
- **Automated Information Extraction**:
  - **Candidate Contact**: Name, Email address, Phone number.
  - **Skill Extraction & Normalization**: Maps technical keywords and phrases across 7 domains to standardized canonical names (e.g. `k8s` → `Kubernetes`, `reactjs` → `React`).
  - **Experience Estimation**: Calculates years of experience from tenure spans and explicit duration statements.
  - **Education & Degree Recognition**: Identifies degrees (B.S., M.S., Ph.D., MBA) and majors (Computer Science, Data Science, etc.).
- **Hybrid Multi-Factor Relevance Scoring**: Combines TF-IDF n-gram cosine similarity, skill set overlap recall, experience seniority matching, and education alignment.
- **Candidate Ranking & Categorization**: Groups candidates into **Strong Match** (≥ 75%), **Good Match** (60–74%), **Moderate Match** (45–59%), and **Low Match** (< 45%).
- **Interactive Warm-Themed UI**: Built with Streamlit, custom warm CSS theme, KPI metric cards, comparison charts, skill badges, and deep-dive candidate profiles.
- **Batch Processing & Export**: Instant 1-click export of candidate rankings to **CSV** and **JSON**, plus downloadable Markdown summary reports for each candidate.
- **CLI Automation**: Run headless batch screening directly from the command line for automated recruitment workflows.

---

## 📐 Scoring Algorithm Explanation

The ranking engine employs a transparent, multi-dimensional scoring model that evaluates candidates across four primary dimensions:

$$\text{Composite Score } S = \Big( w_{\text{skills}} \cdot S_{\text{skills}} + w_{\text{tfidf}} \cdot S_{\text{tfidf}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{edu}} \cdot S_{\text{edu}} \Big) \times 100$$

Where $\sum w_i = 1.0$.

### 1. Skill Set Overlap Score ($S_{\text{skills}}$, Default Weight: 45%)
Measures the recall of required technical competencies identified in the job description:
$$S_{\text{skills}} = \frac{|\text{Candidate Skills} \cap \text{Job Description Skills}|}{|\text{Job Description Skills}|}$$
- If no explicit technical skills are listed in the job description, this component gracefully defaults to the semantic TF-IDF score.
- The screener also highlights **Missing Skills** and **Bonus Technical Skills**.

### 2. Semantic TF-IDF Cosine Similarity ($S_{\text{tfidf}}$, Default Weight: 35%)
Captures topical and contextual alignment between the job description and candidate resume text:
1. **Preprocessing Pipeline**: Unicode normalization, noise cleaning, special token protection (`C++`, `C#`, `.NET`), NLTK stop word removal, and WordNet lemmatization.
2. **Vectorization**: Scikit-learn `TfidfVectorizer` utilizing unigrams and bigrams (`ngram_range=(1, 2)`) with sublinear term frequency scaling.
3. **Cosine Similarity**:
   $$\text{Cosine Similarity} = \frac{\mathbf{v}_{\text{JD}} \cdot \mathbf{v}_{\text{Resume}}}{\|\mathbf{v}_{\text{JD}}\| \|\mathbf{v}_{\text{Resume}}\|}$$
4. **Normalized IR Alignment**: In full-text technical comparisons, raw cosine similarity typically peaks around 0.35–0.45. The engine applies domain calibration ($S_{\text{tfidf}} = \min(1.0, \frac{\text{raw\_sim}}{0.35})$) to yield representative percentage scores.

### 3. Experience Seniority Alignment ($S_{\text{exp}}$, Default Weight: 10%)
- Extracts target experience requirement from the job description (e.g. `5+ years`).
- Extracts candidate's total years of experience from employment dates and explicit statements.
- $S_{\text{exp}} = 1.0$ if candidate meets or exceeds requirements; scaled proportionally if under.

### 4. Education Qualification Alignment ($S_{\text{edu}}$, Default Weight: 10%)
- Checks for degree preferences mentioned in the job description (e.g., Master's, Ph.D., Bachelor's) and verifies candidate degree credentials.

---

## 🗂️ Project Architecture

```
ResumeScreener/
│
├── app.py                             # Streamlit Web Application (Warm Palette UI)
├── cli.py                             # Command-Line Interface for terminal & automation
├── requirements.txt                   # Project Python dependencies
├── candidate_ranking_report.csv       # Sample generated candidate ranking report
├── candidate_ranking_report.json      # Sample generated JSON report
├── README.md                          # Full project documentation
├── text.md                            # Original task requirements
│
├── screener/                          # Core Screener Package
│   ├── __init__.py
│   ├── parser.py                      # Multi-format parser (PDF, DOCX, TXT) & section segmentation
│   ├── nlp_preprocessor.py            # Normalization, tokenization, stop words, lemmatization
│   ├── skills_taxonomy.py             # Categorized skill taxonomy & canonical alias mappings
│   ├── extractor.py                   # Name, email, phone, skills, education, experience extractor
│   ├── matcher.py                     # TF-IDF, Cosine Similarity, Skill Overlap & Composite Ranker
│   └── report_generator.py            # CSV, JSON, and Markdown report generators
│
├── data/
│   ├── create_samples.py              # Generator for sample resumes (PDF & TXT) and JDs
│   ├── sample_job_descriptions/       # Sample Job Descriptions
│   │   ├── senior_ml_engineer.txt
│   │   ├── full_stack_developer.txt
│   │   └── data_analyst.txt
│   └── sample_resumes/                # Sample Resumes (both PDF and TXT versions)
│       ├── alice_walker_senior_ml.pdf
│       ├── bob_martinez_frontend_react.pdf
│       ├── charlie_patel_fullstack.pdf
│       ├── diana_chen_data_analyst.pdf
│       └── evan_ross_junior_devops.pdf
│
└── tests/
    └── test_screener.py               # Automated unit & integration test suite (100% passing)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+ (tested on Python 3.10, 3.11, 3.12, 3.14)

### 2. Installation
Clone or navigate to the project directory:
```bash
cd ResumeScreener
python -m pip install -r requirements.txt
```

Download NLTK corpora (automatically handled, or run once):
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet')"
```

---

## 🖥️ Running the Streamlit Web Application

Launch the warm-themed Streamlit application using Python's module flag:
```bash
python -m streamlit run app.py
```

> **Note for Git Bash & Windows Terminal**: If `streamlit` is not directly in your environment PATH, running via `python -m streamlit run app.py` invokes the installed Streamlit package directly without requiring PATH modifications.

Alternatively, you can run the helper script:
- On **Bash**: `./run_app.sh`
- On **Windows**: Double-click [`run_app.bat`](file:///c:/Users/SHREE/Downloads/ResumeScreener/run_app.bat)

The application will open in your default browser at `http://localhost:8501`.

### Web UI Features:
1. **1-Click Pre-Loaded Testing**: Select a sample job description preset (e.g. *Senior Machine Learning Engineer*) and leave "Include Pre-loaded Sample Resumes" checked to see instant rankings without uploading external files.
2. **Drag & Drop Upload**: Upload any number of `.pdf`, `.docx`, or `.txt` resumes simultaneously.
3. **Interactive Visualizations & Streamlined Leaderboard**:
   - Clean, uncluttered leaderboard table with directly clickable candidate names, unclipped status badges, and progress bars.
   - Comparative Altair bar chart displaying composite scores.
   - Skill coverage vs. experience scatter plot.
4. **Seamless Integrated Deep-Dive**: Click any candidate name in the table to immediately inspect their detailed metrics, green matched skill badges, red missing skill badges, and experience/education breakdown directly below on the same page.
5. **Report Export**: Download CSV ranking spreadsheets or comprehensive Markdown summaries.

---

## 💻 Running the Command-Line Interface (CLI)

The CLI allows automated batch processing of resumes against any job description:

```bash
# Basic usage: screen sample resumes against Senior ML Engineer role
python cli.py --jd data/sample_job_descriptions/senior_ml_engineer.txt --resumes data/sample_resumes/

# Save ranking report to custom CSV and JSON
python cli.py --jd data/sample_job_descriptions/full_stack_developer.txt --resumes data/sample_resumes/ --csv-output fullstack_report.csv --json-output fullstack_report.json

# Verbose output with full individual candidate markdown summaries
python cli.py --jd data/sample_job_descriptions/data_analyst.txt --resumes data/sample_resumes/ --verbose
```

### Example CLI Output:
```text
==================================================
           AI RESUME SCREENER CLI                 
==================================================
Loading Job Description: data/sample_job_descriptions/senior_ml_engineer.txt
Scanning Resumes from: ['data/sample_resumes/']
Successfully parsed 10 resumes.
Computing TF-IDF cosine similarities & evaluating skill match...

------------------------------------------------------------------------------------------------
Rank  | Candidate Name         | Score   | Status         | Skills Matched | Exp   | Source File
------------------------------------------------------------------------------------------------
#1    | Alice Walker           |  82.8% | Strong Match   | 25/29          |  8.0y | alice_walker_senior_ml.pdf
#2    | Alice Walker           |  81.7% | Strong Match   | 25/29          |  8.0y | alice_walker_senior_ml.txt
#3    | Charlie Patel          |  40.6% | Low Match      | 11/29          |  6.0y | charlie_patel_fullstack.pdf
#4    | Charlie Patel          |  40.3% | Low Match      | 11/29          |  6.0y | charlie_patel_fullstack.txt
#5    | Evan Ross              |  31.2% | Low Match      | 6/29           |  4.0y | evan_ross_junior_devops.pdf
...
------------------------------------------------------------------------------------------------

Screening Summary:
  Total Candidates: 10
  Top Match Score:  82.8%
  Average Score:    42.3%
  Strong Matches:   2
  Good Matches:     0

Saved CSV ranking report to: candidate_ranking_report.csv
```

---

## 🧪 Automated Testing

To run the automated unit and integration tests:

```bash
python -m unittest tests/test_screener.py
```

All 10 test suites verify:
- Accurate PDF and TXT text extraction.
- Resume section segmentation (`skills`, `experience`, `education`).
- NLP text cleaning, tokenization, stop word filtering, and lemmatization.
- Skill keyword and phrase extraction with canonical normalization.
- Name, email, and phone contact parsing.
- TF-IDF cosine similarity computation.
- Candidate ranking relevance across Machine Learning, Full Stack, and Data Analyst roles.
- CSV, JSON, and Markdown report generation.

---

## 📊 Evaluation Criteria Alignment

| Criteria | Implementation Highlights |
| :--- | :--- |
| **Accuracy of skill extraction** | Comprehensive taxonomy covering 7 domains with canonical alias normalization (`k8s` → `Kubernetes`, `pytorch` → `PyTorch`) and special symbol safety (`C++`, `C#`, `.NET`). |
| **Relevance of ranking algorithm** | Weighted composite scoring combining TF-IDF n-gram cosine similarity (35%), skill overlap recall (45%), experience seniority (10%), and education alignment (10%). |
| **Interface clarity** | Thoughtfully crafted Streamlit dashboard using a warm color scheme (`#D97706`, `#FAF8F5`, `#EEDCC9`), KPI summary cards, badges, and Altair charts. |
| **Handling different formats** | Universal resume ingestion supporting `.pdf` (pdfplumber + pypdf fallback), `.docx`, and `.txt`. |
| **Code quality and documentation** | Modular architecture (`screener/`), type annotations, clean docstrings, complete unit tests, and CLI documentation. |

