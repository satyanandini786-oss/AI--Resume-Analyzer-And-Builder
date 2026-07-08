"""
app.py
Streamlit entry point for the AI Resume Analyzer & Builder.
Run with: streamlit run app.py
"""

import os
import streamlit as st

from analyzer import analyze_resume
from builder import build_resume, parse_comma_list
from utils import extract_text

st.set_page_config(page_title="AI Resume Analyzer & Builder", page_icon="📄", layout="wide")

st.sidebar.title("📄 AI Resume Toolkit")
page = st.sidebar.radio("Go to", ["Resume Analyzer", "Resume Builder"])


# --------------------------------------------------------------------------
# PAGE 1: RESUME ANALYZER
# --------------------------------------------------------------------------
if page == "Resume Analyzer":
    st.title("🔍 AI Resume Analyzer")
    st.write("Upload your resume to get an ATS score, job-fit matches, skill gaps, and interview prep.")

    uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    job_description = st.text_area("Paste a job description (optional, improves ATS scoring)", height=150)

    if uploaded_file is not None:
        os.makedirs("resumes", exist_ok=True)
        temp_path = os.path.join("resumes", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        resume_text = extract_text(temp_path)

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing..."):
                results = analyze_resume(resume_text, job_description)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📇 Contact Info Detected")
                st.write(f"Email: {results['email'] or 'Not found'}")
                st.write(f"Phone: {results['phone'] or 'Not found'}")

                st.subheader("🛠 Skills Found")
                if results["skills_found"]:
                    st.write(", ".join(results["skills_found"]))
                else:
                    st.write("No known skills detected — consider adding a Skills section.")

            with col2:
                if results["ats_score"] is not None:
                    st.subheader("🎯 ATS Match Score")
                    st.metric("Score vs job description", f"{results['ats_score']}%")
                st.subheader("🏆 Best Matching Role")
                st.write(results["best_role"] or "No match found")

            st.subheader("📊 Top Job Role Matches")
            st.dataframe(results["job_matches"], use_container_width=True)

            st.subheader("📚 Recommended Courses (for your skill gaps)")
            if not results["course_recommendations"].empty:
                st.dataframe(results["course_recommendations"], use_container_width=True)
            else:
                st.write("No gaps found in our course database — nice work!")

            st.subheader("🎤 Interview Questions to Practice")
            if not results["interview_questions"].empty:
                for _, row in results["interview_questions"].iterrows():
                    st.markdown(f"- **[{row['category']}]** {row['question']}")
            else:
                st.write("No questions found for this role yet.")


# --------------------------------------------------------------------------
# PAGE 2: RESUME BUILDER
# --------------------------------------------------------------------------
elif page == "Resume Builder":
    st.title("🛠 AI Resume Builder")
    st.write("Fill in your details and generate a polished .docx resume instantly.")

    template_name = st.selectbox("Choose a template", ["Modern", "Professional"])

    with st.form("resume_form"):
        st.subheader("Basic Info")
        name = st.text_input("Full Name")
        title = st.text_input("Professional Title (e.g. Data Science Student)")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        location = st.text_input("Location (City, State)")
        linkedin = st.text_input("LinkedIn URL")
        github = st.text_input("GitHub URL")

        st.subheader("Summary")
        summary = st.text_area("Professional Summary", height=100)

        st.subheader("Skills")
        skills_raw = st.text_input("Skills (comma-separated)", placeholder="Python, SQL, Power BI, Tableau")

        st.subheader("Education")
        edu_degree = st.text_input("Degree", placeholder="B.Sc. Data Science")
        edu_school = st.text_input("College/University")
        edu_year = st.text_input("Year")
        edu_score = st.text_input("CGPA / Percentage")

        st.subheader("Projects (up to 3)")
        proj_rows = []
        for i in range(1, 4):
            with st.expander(f"Project {i}"):
                p_title = st.text_input(f"Project {i} Title", key=f"pt{i}")
                p_desc = st.text_area(f"Project {i} Description", key=f"pd{i}", height=70)
                p_tech = st.text_input(f"Project {i} Tech Used", key=f"ptech{i}")
                p_link = st.text_input(f"Project {i} Link", key=f"plink{i}")
                if p_title:
                    proj_rows.append({
                        "title": p_title, "description": p_desc,
                        "tech": p_tech, "link": p_link
                    })

        st.subheader("Certifications")
        certs_raw = st.text_area("Certifications (one per line)", height=80)

        submitted = st.form_submit_button("Generate Resume")

    if submitted:
        data = {
            "name": name,
            "title": title,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "github": github,
            "summary": summary,
            "skills": parse_comma_list(skills_raw),
            "education": [{
                "degree": edu_degree, "school": edu_school,
                "year": edu_year, "score": edu_score
            }] if edu_degree or edu_school else [],
            "projects": proj_rows,
            "certifications": [c.strip() for c in certs_raw.split("\n") if c.strip()],
            "experience": [],  # extend this section if the user has work experience
        }

        with st.spinner("Building your resume..."):
            output_path = build_resume(data, template_name=template_name)

        st.success("Resume generated!")
        with open(output_path, "rb") as f:
            st.download_button(
                label="⬇ Download Resume (.docx)",
                data=f,
                file_name=os.path.basename(output_path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )