"""
Skills Taxonomy and Canonical Dictionary for Resume Screening.
Includes domain categorizations, keyword variations, and alias mappings.
"""

# Categorized taxonomy for domain-specific insights
SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "c", "javascript", "typescript", "go",
        "rust", "ruby", "php", "swift", "kotlin", "sql", "r", "scala", "shell",
        "bash", "powershell", "dart", "matlab", "perl", "html", "css", "sass"
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "next.js", "nuxt", "node.js", "express",
        "django", "fastapi", "flask", "spring boot", "spring", "asp.net", ".net",
        "ruby on rails", "graphql", "rest api", "tailwind css", "bootstrap",
        "jquery", "redux", "svelte", "flutter", "react native"
    ],
    "Data Science & AI / ML": [
        "machine learning", "deep learning", "natural language processing", "nlp",
        "computer vision", "llm", "large language models", "generative ai",
        "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy",
        "scipy", "hugging face", "transformers", "langchain", "llamaindex",
        "data analysis", "data mining", "statistical analysis", "data visualization",
        "matplotlib", "seaborn", "tableau", "power bi", "apache spark", "spark",
        "hadoop", "opencv", "reinforcement learning", "feature engineering"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp",
        "google cloud platform", "docker", "kubernetes", "k8s", "terraform",
        "ci/cd", "jenkins", "github actions", "gitlab ci", "ansible", "puppet",
        "chef", "linux", "unix", "prometheus", "grafana", "helm", "serverless",
        "microservices", "nginx", "apache", "cloudformation"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "sqlite", "oracle", "cassandra", "dynamodb", "snowflake", "bigquery",
        "redshift", "neo4j", "mariadb", "firebase", "supabase"
    ],
    "Tools & Methodologies": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "devops", "tdd", "test driven development",
        "unit testing", "system design", "software architecture", "restful",
        "ci/cd pipelines", "code review", "debugging"
    ],
    "Soft Skills & Leadership": [
        "leadership", "team leadership", "mentorship", "communication",
        "collaboration", "problem solving", "critical thinking", "project management",
        "time management", "stakeholder management", "cross-functional team"
    ]
}

# Mapping aliases/variants to canonical names
CANONICAL_SKILL_MAP = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "sklearn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "keras": "Keras",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "computer vision": "Computer Vision",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "llm": "LLM",
    "large language models": "LLM",
    "large language model": "LLM",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "rest api": "REST API",
    "restful": "REST API",
    "graphql": "GraphQL",
    "linux": "Linux",
    "terraform": "Terraform",
    "jenkins": "Jenkins",
    "sql": "SQL",
    "mysql": "MySQL",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "snowflake": "Snowflake",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "hadoop": "Hadoop",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "php": "PHP",
    "html": "HTML",
    "css": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "microservices": "Microservices",
    "unit testing": "Unit Testing",
    "tdd": "TDD",
    "system design": "System Design",
}

# Create a flattened set of all skill keywords for fast regex/matching
ALL_SKILL_KEYWORDS = set()
for cat, skills in SKILL_CATEGORIES.items():
    for s in skills:
        ALL_SKILL_KEYWORDS.add(s.lower())

for alias in CANONICAL_SKILL_MAP.keys():
    ALL_SKILL_KEYWORDS.add(alias.lower())

def get_canonical_skill(skill_str: str) -> str:
    """Normalize skill name to standard capitalized/formatted canonical name."""
    cleaned = skill_str.strip().lower()
    if cleaned in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[cleaned]
    # Check if capitalized version exists in taxonomy
    for cat, skills in SKILL_CATEGORIES.items():
        for s in skills:
            if s.lower() == cleaned:
                return s.title()
    return skill_str.strip().title()

def get_skill_category(skill_canonical: str) -> str:
    """Return the domain category for a canonical skill name."""
    skill_lower = skill_canonical.lower()
    for cat, skills in SKILL_CATEGORIES.items():
        if any(s.lower() == skill_lower for s in skills):
            return cat
    # Check alias maps
    for alias, canonical in CANONICAL_SKILL_MAP.items():
        if canonical.lower() == skill_lower:
            for cat, skills in SKILL_CATEGORIES.items():
                if any(s.lower() == alias.lower() for s in skills):
                    return cat
    return "Other Technical Skills"

