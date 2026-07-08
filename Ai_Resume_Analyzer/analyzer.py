"""
analyzer.py
Core logic for the Resume Analyzer: ATS scoring, job-role matching,
skill-gap detection, course recommendations, and interview prep questions.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import extract_skills, extract_email, extract_phone, clean_text


def load_jobs(path="jobs.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["required_skills_list"] = df["required_skills"].apply(
        lambda s: [skill.strip().lower() for skill in s.split(",")]
    )
    return df


def load_courses(path="courses.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def load_interview_questions(path="interview_questions.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def calculate_ats_score(resume_text: str, job_description: str) -> float:
    """
    Compute a similarity score (0-100) between a resume and a job description
    using TF-IDF + cosine similarity. This mimics a basic ATS keyword match.
    """
    if not job_description.strip():
        return 0.0

    documents = [clean_text(resume_text), clean_text(job_description)]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)


def match_jobs(resume_skills: list, jobs_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Rank job roles by percentage overlap between resume skills and each
    role's required skills. Returns the top_n matches with match % and
    missing skills for each.
    """
    resume_skills_set = set(s.lower() for s in resume_skills)
    results = []

    for _, row in jobs_df.iterrows():
        required = set(row["required_skills_list"])
        if not required:
            continue
        matched = resume_skills_set & required
        missing = required - resume_skills_set
        match_pct = round(len(matched) / len(required) * 100, 1)
        results.append({
            "job_title": row["job_title"],
            "match_percent": match_pct,
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "experience_level": row.get("experience_level", "")
        })

    results_df = pd.DataFrame(results).sort_values(
        "match_percent", ascending=False
    ).reset_index(drop=True)
    return results_df.head(top_n)


def recommend_courses(missing_skills: list, courses_df: pd.DataFrame) -> pd.DataFrame:
    """Return course recommendations for a given list of missing skills."""
    if not missing_skills:
        return pd.DataFrame(columns=courses_df.columns)
    mask = courses_df["skill"].str.lower().isin([s.lower() for s in missing_skills])
    return courses_df[mask].reset_index(drop=True)


def get_interview_questions(job_title: str, questions_df: pd.DataFrame) -> pd.DataFrame:
    """Return interview questions relevant to a given job title."""
    mask = questions_df["job_title"].str.lower() == job_title.lower()
    return questions_df[mask].reset_index(drop=True)


def analyze_resume(resume_text: str, job_description: str = "") -> dict:
    """
    Full analysis pipeline used by app.py:
    1. Extract skills, email, phone from resume text
    2. Score against a job description (if provided)
    3. Match against known job roles
    4. Recommend courses for missing skills of the best-matched role
    5. Pull interview questions for the best-matched role
    """
    jobs_df = load_jobs()
    courses_df = load_courses()
    questions_df = load_interview_questions()

    skills = extract_skills(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)

    ats_score = calculate_ats_score(resume_text, job_description) if job_description else None
    job_matches = match_jobs(skills, jobs_df, top_n=5)

    best_role = job_matches.iloc[0]["job_title"] if not job_matches.empty else None
    missing_skills = job_matches.iloc[0]["missing_skills"] if not job_matches.empty else []

    course_recs = recommend_courses(missing_skills, courses_df)
    interview_qs = get_interview_questions(best_role, questions_df) if best_role else pd.DataFrame()

    return {
        "email": email,
        "phone": phone,
        "skills_found": skills,
        "ats_score": ats_score,
        "job_matches": job_matches,
        "best_role": best_role,
        "missing_skills": missing_skills,
        "course_recommendations": course_recs,
        "interview_questions": interview_qs,
    }