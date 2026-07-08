"""
utils.py
Shared helper functions used by analyzer.py and builder.py
"""

import re

# A master skill list used for keyword extraction from resumes.
# Extend this list any time you want the analyzer to recognize more skills.
MASTER_SKILLS = [
    "python", "sql", "java", "c++", "html", "css", "javascript", "react",
    "django", "flask", "excel", "power bi", "tableau", "dax", "statistics",
    "machine learning", "deep learning", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "git",
    "github", "api", "dbms", "etl", "spark", "airflow", "cloud", "aws",
    "azure", "gcp", "nlp", "data visualization", "data modeling",
    "communication", "leadership", "problem solving", "streamlit"
]


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF resume."""
    import PyPDF2
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from a DOCX resume."""
    import docx2txt
    return docx2txt.process(file_path)


def extract_text(file_path: str) -> str:
    """Detect file type by extension and extract text accordingly."""
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")


def clean_text(text: str) -> str:
    """Lowercase and strip extra whitespace/special characters for matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text: str, skill_list=None) -> list:
    """Return the list of known skills found inside the given text."""
    if skill_list is None:
        skill_list = MASTER_SKILLS
    cleaned = clean_text(text)
    found = [skill for skill in skill_list if skill in cleaned]
    return sorted(set(found))


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"(\+?\d{1,3}[-\s]?)?\d{10}", text)
    return match.group(0) if match else ""