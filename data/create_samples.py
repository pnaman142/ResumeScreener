"""
Script to generate sample Job Descriptions and Resumes (both TXT and PDF formats).
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
JD_DIR = os.path.join(DATA_DIR, "sample_job_descriptions")
RESUME_DIR = os.path.join(DATA_DIR, "sample_resumes")

os.makedirs(JD_DIR, exist_ok=True)
os.makedirs(RESUME_DIR, exist_ok=True)

# ----------------- Job Descriptions -----------------
JOB_DESCRIPTIONS = {
    "senior_ml_engineer.txt": """Job Title: Senior Machine Learning Engineer
Department: Artificial Intelligence & Research
Location: Remote / Hybrid
Experience Required: 5+ years of experience
Education: Bachelor's or Master's degree in Computer Science, Data Science, or related field.

About the Role:
We are seeking an experienced Senior Machine Learning Engineer to design, build, and deploy production-grade machine learning models and NLP pipelines. You will collaborate with cross-functional teams to integrate generative AI, deep learning models, and automated inference services into our scalable cloud platform.

Key Responsibilities:
- Design, train, evaluate, and deploy machine learning and deep learning models at scale.
- Develop Natural Language Processing (NLP) solutions and large language model (LLM) pipelines.
- Implement robust data preprocessing, feature engineering, and model validation workflows.
- Containerize models using Docker and orchestrate deployments on Kubernetes and AWS cloud infrastructure.
- Build CI/CD pipelines for automated retraining, testing, and continuous deployment.
- Maintain high code quality through unit testing, code reviews, and Agile methodologies.

Required Technical Skills:
- Programming: Python, SQL, C++
- Frameworks & Libraries: PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, Hugging Face, Transformers
- Core Domains: Machine Learning, Deep Learning, NLP, Computer Vision
- Cloud & Infrastructure: AWS, Docker, Kubernetes, CI/CD, Linux, Git
- Methodologies: Agile, Scrum, Unit Testing, System Design
""",

    "full_stack_developer.txt": """Job Title: Full Stack Developer
Department: Engineering
Location: New York, NY / Remote
Experience Required: 3+ years of experience
Education: Bachelor's degree in Computer Science, Software Engineering, or equivalent.

About the Role:
We are looking for a skilled Full Stack Developer to build modern, responsive web applications and scalable backend APIs. The ideal candidate has strong expertise in modern JavaScript/TypeScript, React, Node.js, and relational databases.

Key Responsibilities:
- Develop intuitive, high-performance web frontends using React, TypeScript, and modern CSS frameworks like Tailwind CSS.
- Design and implement secure, scalable backend REST APIs and microservices using Node.js and Express.
- Manage database schemas, queries, and migrations using PostgreSQL and Redis caching.
- Package applications into Docker containers and integrate with automated CI/CD pipelines.
- Collaborate with product managers and designers in an Agile scrum environment.

Required Technical Skills:
- Frontend: JavaScript, TypeScript, React, Next.js, HTML, CSS, Tailwind CSS, Redux
- Backend: Node.js, Express, REST API, GraphQL
- Databases: PostgreSQL, MongoDB, Redis
- DevOps & Tools: Docker, Git, GitHub Actions, Linux, CI/CD
- Methodologies: Agile, Scrum, Unit Testing
""",

    "data_analyst.txt": """Job Title: Data Analyst
Department: Business Intelligence
Location: Chicago, IL / Hybrid
Experience Required: 2+ years of experience
Education: Bachelor's degree in Statistics, Mathematics, Computer Science, or Business.

About the Role:
We are seeking a detail-oriented Data Analyst to transform complex raw datasets into actionable business intelligence. You will build interactive dashboards, perform statistical analysis, and generate reports that empower executive decision-making.

Key Responsibilities:
- Extract, clean, and analyze data across multiple relational and cloud data warehouses.
- Build dynamic, visual dashboards using Tableau and Power BI.
- Write complex SQL queries for aggregation, window functions, and data transformations.
- Perform exploratory data analysis and statistical modeling using Python and Pandas.
- Present findings clearly to stakeholders and cross-functional leadership teams.

Required Technical Skills:
- Analytics: Data Analysis, Statistical Analysis, Data Visualization, Data Mining
- Tools: SQL, Python, Pandas, NumPy, Tableau, Power BI, Excel
- Soft Skills: Communication, Problem Solving, Critical Thinking, Project Management
"""
}

# ----------------- Sample Candidates -----------------
CANDIDATES = [
    {
        "filename": "alice_walker_senior_ml.txt",
        "pdf_name": "alice_walker_senior_ml.pdf",
        "name": "Alice Walker",
        "email": "alice.walker@email.com",
        "phone": "+1 (555) 345-6789",
        "title": "Senior Machine Learning Engineer",
        "years": "6 years of experience",
        "text": """Alice Walker
alice.walker@email.com | +1 (555) 345-6789 | San Francisco, CA | linkedin.com/in/alicewalker

PROFESSIONAL SUMMARY
Senior Machine Learning Engineer with 6+ years of experience architecting end-to-end ML and deep learning pipelines. Proven expertise in PyTorch, TensorFlow, NLP transformers, and deploying scalable inference systems on AWS and Kubernetes.

TECHNICAL SKILLS
- Programming Languages: Python, SQL, C++, Bash
- ML & Deep Learning: PyTorch, TensorFlow, Scikit-learn, Hugging Face, Transformers, NLP, Deep Learning, Machine Learning, Pandas, NumPy, SciPy
- Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Git, Linux
- Databases: PostgreSQL, Redis, MongoDB
- Methodologies: Agile, Scrum, Unit Testing, System Design

WORK EXPERIENCE
Senior Machine Learning Engineer | Nova AI Systems | 2021 - Present
- Designed and deployed transformer-based NLP models serving 10M+ daily API inference requests with PyTorch and Hugging Face.
- Built automated continuous training CI/CD pipelines using Docker, Kubernetes, and AWS SageMaker.
- Reduced model latency by 45% through quantization and TensorRT optimizations.
- Mentored junior engineers and led Agile sprint planning sessions.

Machine Learning Engineer | Apex Data Labs | 2018 - 2021
- Developed predictive classification and regression models using Scikit-learn and XGBoost.
- Engineered automated data pipelines in Python and SQL handling over 500GB of daily telemetry.
- Containerized microservices using Docker and deployed to Linux environments.

EDUCATION
Master of Science in Computer Science | Stanford University | 2018
Bachelor of Science in Computer Science | UC Berkeley | 2016

CERTIFICATIONS
- AWS Certified Machine Learning - Specialty
- Deep Learning Specialization (DeepLearning.AI)
"""
    },
    {
        "filename": "bob_martinez_frontend_react.txt",
        "pdf_name": "bob_martinez_frontend_react.pdf",
        "name": "Bob Martinez",
        "email": "bob.martinez@email.com",
        "phone": "+1 (555) 890-1234",
        "title": "Lead Frontend React Engineer",
        "years": "5 years of experience",
        "text": """Bob Martinez
bob.martinez@email.com | +1 (555) 890-1234 | Austin, TX | github.com/bobmartinez

PROFESSIONAL SUMMARY
Creative and user-obsessed Lead Frontend Engineer with 5+ years of experience crafting rich web applications using React, TypeScript, Next.js, and modern styling systems.

TECHNICAL SKILLS
- Languages: JavaScript, TypeScript, HTML, CSS, Sass
- Frameworks & Libraries: React, Next.js, Redux, Tailwind CSS, Bootstrap, Node.js
- Tools & DevOps: Git, GitHub Actions, Docker, Webpack, Vite, Jest
- Methodologies: Agile, Scrum, Unit Testing, UI/UX Design

WORK EXPERIENCE
Lead Frontend Engineer | PixelCraft Studios | 2022 - Present
- Led frontend architecture for high-traffic SaaS portal using React 18, TypeScript, and Next.js.
- Developed modular UI component library in Tailwind CSS with 100% test coverage using Jest.
- Improved Core Web Vitals and Lighthouse page performance scores from 64 to 98.

Frontend Developer | Horizon Web Agency | 2019 - 2022
- Built responsive client web applications using React, Redux, and REST API integrations.
- Collaborated closely with UI/UX designers to translate Figma mockups into accessible interfaces.
- Managed version control with Git and established CI/CD deployments via GitHub Actions.

EDUCATION
Bachelor of Science in Software Engineering | University of Texas at Austin | 2019
"""
    },
    {
        "filename": "charlie_patel_fullstack.txt",
        "pdf_name": "charlie_patel_fullstack.pdf",
        "name": "Charlie Patel",
        "email": "charlie.patel@email.com",
        "phone": "+1 (555) 456-7890",
        "title": "Senior Full Stack Developer",
        "years": "4 years of experience",
        "text": """Charlie Patel
charlie.patel@email.com | +1 (555) 456-7890 | Seattle, WA | github.com/charliepatel

PROFESSIONAL SUMMARY
Full Stack Software Developer with 4+ years of hands-on experience building scalable web solutions across frontend and backend tiers using React, Node.js, TypeScript, PostgreSQL, and Docker.

TECHNICAL SKILLS
- Programming Languages: TypeScript, JavaScript, Python, SQL, HTML, CSS
- Frontend: React, Next.js, Tailwind CSS, Redux
- Backend: Node.js, Express, REST API, GraphQL, FastAPI
- Databases: PostgreSQL, MongoDB, Redis
- Cloud & Tools: Docker, AWS, Git, CI/CD, GitHub Actions, Linux
- Practices: Agile, Scrum, Unit Testing, System Design

WORK EXPERIENCE
Full Stack Engineer | CloudScale Inc. | 2021 - Present
- Architected enterprise SaaS platform using React, Node.js, Express, and PostgreSQL.
- Implemented real-time synchronization with WebSockets and Redis caching layer.
- Deployed microservices on AWS with Docker containers and automated GitHub Actions CI/CD.
- Designed RESTful API endpoints and GraphQL schemas serving 500,000+ active users.

Junior Software Developer | CodeWave Solutions | 2020 - 2021
- Developed responsive UI screens using React and CSS modules.
- Created CRUD API services in Node.js with MongoDB database persistence.
- Participated in Agile daily standups, code reviews, and unit testing.

EDUCATION
Bachelor of Science in Computer Science | University of Washington | 2020
"""
    },
    {
        "filename": "diana_chen_data_analyst.txt",
        "pdf_name": "diana_chen_data_analyst.pdf",
        "name": "Diana Chen",
        "email": "diana.chen@email.com",
        "phone": "+1 (555) 789-0123",
        "title": "Senior Data Analyst",
        "years": "3.5 years of experience",
        "text": """Diana Chen
diana.chen@email.com | +1 (555) 789-0123 | Boston, MA | linkedin.com/in/dianachen

PROFESSIONAL SUMMARY
Results-driven Data Analyst with 3+ years of experience extracting business insights from large-scale structured data. Advanced expertise in SQL, Python, Tableau, Power BI, and statistical modeling.

TECHNICAL SKILLS
- Analytics & Modeling: Data Analysis, Statistical Analysis, Data Visualization, Data Mining
- Programming & DB: SQL, Python, Pandas, NumPy, PostgreSQL, Snowflake
- BI & Visualization Tools: Tableau, Power BI, Excel, Matplotlib, Seaborn
- Methodologies: Agile, Problem Solving, Project Management, Communication

WORK EXPERIENCE
Data Analyst | Beacon Financial Group | 2022 - Present
- Built 15+ automated Tableau and Power BI executive dashboards tracking $20M quarterly revenue.
- Authored complex SQL queries on Snowflake and PostgreSQL to aggregate customer behavior metrics.
- Applied exploratory data analysis with Python (Pandas, NumPy) to optimize churn prediction.
- Partnered with product and marketing stakeholders to define key performance indicators (KPIs).

Junior Business Intelligence Analyst | Metrix Consulting | 2021 - 2022
- Conducted variance analysis and statistical summaries in Excel and SQL.
- Designed recurring automated reporting pipelines reducing weekly manual reporting time by 60%.

EDUCATION
Bachelor of Science in Statistics and Mathematics | Boston University | 2021
"""
    },
    {
        "filename": "evan_ross_junior_devops.txt",
        "pdf_name": "evan_ross_junior_devops.pdf",
        "name": "Evan Ross",
        "email": "evan.ross@email.com",
        "phone": "+1 (555) 234-5678",
        "title": "Junior DevOps & Cloud Engineer",
        "years": "2 years of experience",
        "text": """Evan Ross
evan.ross@email.com | +1 (555) 234-5678 | Denver, CO | github.com/evanross

PROFESSIONAL SUMMARY
DevOps Engineer with 2 years of experience supporting cloud infrastructure, CI/CD automation, containerization, and Linux system administration.

TECHNICAL SKILLS
- Cloud Platforms: AWS, GCP
- Containers & Orchestration: Docker, Kubernetes, Helm
- CI/CD & Automation: Jenkins, GitHub Actions, Terraform, Ansible, Bash
- Programming & Scripting: Python, Shell, Linux
- Monitoring: Prometheus, Grafana

WORK EXPERIENCE
Junior DevOps Engineer | Stratus Cloud Tech | 2022 - Present
- Provisioned infrastructure as code (IaC) using Terraform on AWS.
- Configured Docker build files and deployed applications into Kubernetes clusters.
- Automated CI/CD build and test pipelines using GitHub Actions and Jenkins.
- Maintained monitoring and alert dashboards using Prometheus and Grafana.

EDUCATION
Bachelor of Science in Information Technology | University of Colorado Boulder | 2022
"""
    }
]


def write_txt_files():
    for filename, content in JOB_DESCRIPTIONS.items():
        path = os.path.join(JD_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Created JD: {path}")

    for c in CANDIDATES:
        path = os.path.join(RESUME_DIR, c["filename"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(c["text"].strip())
        print(f"Created Resume TXT: {path}")


def generate_pdf_resume(candidate_info, output_path):
    """Generate high quality, beautiful styled PDF resume."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    # Custom styles with warm accent palette
    primary_color = colors.HexColor("#9A3412")  # Warm terracotta / rust
    text_color = colors.HexColor("#1F2937")     # Dark charcoal slate
    accent_bar = colors.HexColor("#F97316")     # Warm orange

    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        "ResumeSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=text_color,
        spaceAfter=6
    )

    story = []
    # Header
    story.append(Paragraph(candidate_info["name"], name_style))
    contact_line = f"{candidate_info['email']} | {candidate_info['phone']} | {candidate_info['title']}"
    story.append(Paragraph(contact_line, contact_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_bar, spaceAfter=10))

    # Parse sections from candidate text
    text = candidate_info["text"]
    lines = text.split("\n")
    i = 0
    current_sec = ""
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line in ["PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "WORK EXPERIENCE", "EDUCATION", "CERTIFICATIONS"]:
            story.append(Paragraph(line, section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=6))
        elif line.startswith("- "):
            story.append(Paragraph(f"• {line[2:]}", body_style))
        elif "|" in line and ("Present" in line or "20" in line or "University" in line):
            bold_style = ParagraphStyle("RoleHeading", parent=body_style, fontName="Helvetica-Bold")
            story.append(Paragraph(line, bold_style))
        else:
            if not line.startswith(candidate_info["name"]) and "@" not in line:
                story.append(Paragraph(line, body_style))
        i += 1

    doc.build(story)
    print(f"Generated PDF Resume: {output_path}")


def main():
    write_txt_files()
    for c in CANDIDATES:
        pdf_path = os.path.join(RESUME_DIR, c["pdf_name"])
        generate_pdf_resume(c, pdf_path)
    print("All sample datasets successfully generated!")


if __name__ == "__main__":
    main()

