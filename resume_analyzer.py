import re
from io import BytesIO

import streamlit as st

import database as db
from ai_service import ai


KEYWORDS = {
    "TCS": ["Java", "SQL", "OOP", "Aptitude", "Communication", "SDLC"],
    "Infosys": ["Python", "Java", "DBMS", "Problem Solving", "Agile"],
    "Wipro": ["Programming", "Testing", "Cloud", "SQL", "Communication"],
    "Accenture": ["Consulting", "Cloud", "Data", "Agile", "Problem Solving"],
    "Capgemini": ["Java", "SQL", "Analytical", "SDLC", "Teamwork"],
    "Cognizant": ["Java", "Testing", "SQL", "Web", "Communication"],
    "Deloitte": ["Analytics", "Consulting", "SQL", "Presentation", "Business"],
    "Amazon": ["DSA", "System Design", "Leadership", "Ownership", "Scalability"],
    "Microsoft": ["DSA", "OOP", "Cloud", "Problem Solving", "Projects"],
    "Google": ["Algorithms", "Data Structures", "Distributed Systems", "Optimization"],
    "Salesforce": ["CRM", "Apex", "Cloud", "JavaScript", "Customer Success"],
}


def extract_pdf_text(uploaded_file) -> str:
    data = uploaded_file.read()
    text = ""
    try:
        import pdfplumber

        with pdfplumber.open(BytesIO(data)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        try:
            import PyPDF2

            reader = PyPDF2.PdfReader(BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            text = ""
    return text.strip()


def score_resume(text, target_company, skills):
    words = re.findall(r"[A-Za-z+#.]+", text)
    lower = text.lower()
    company_keywords = KEYWORDS.get(target_company, [])
    skill_terms = [s.strip() for s in skills.split(",") if s.strip()]
    all_keywords = company_keywords + skill_terms + ["project", "internship", "achievement", "github", "education"]
    present = [kw for kw in all_keywords if kw.lower() in lower]
    missing = [kw for kw in all_keywords if kw.lower() not in lower]
    sections = sum(1 for s in ["education", "skills", "projects", "experience", "achievements"] if s in lower)
    metrics = len(re.findall(r"\d+%?|\b\d+\b", text))
    action_verbs = sum(1 for v in ["built", "developed", "designed", "improved", "reduced", "created", "implemented"] if v in lower)
    ats = min(95, 35 + sections * 8 + min(metrics, 8) * 3 + min(action_verbs, 8) * 3 + len(present) * 2)
    skills_match = int((len(present) / max(len(all_keywords), 1)) * 100)
    grammar_issues = max(0, text.count("  ") + len(re.findall(r"\bi\b", text)))
    return {
        "ats_score": int(ats),
        "skills_match": skills_match,
        "missing_keywords": missing[:10],
        "grammar_issues": grammar_issues,
        "project_quality": "Strong" if "project" in lower and metrics else "Add project impact, tech stack, and metrics.",
        "experience_quality": "Good" if "intern" in lower or "experience" in lower else "Add internship, volunteering, or academic project responsibilities.",
        "formatting": "Good" if len(words) > 150 and sections >= 3 else "Use clear sections: Education, Skills, Projects, Experience, Achievements.",
        "improvements": [
            "Start each bullet with an action verb.",
            "Add numbers such as accuracy, users, latency, time saved, or rank.",
            "Match keywords to the selected company role.",
            "Keep bullets under two lines and avoid paragraphs.",
        ],
    }


def render_resume_analyzer(user):
    st.title("Resume Analyzer")
    st.caption("Upload a PDF resume and get ATS-style feedback, keyword gaps, and improvement ideas.")
    target_company = st.selectbox("Target company", db.COMPANIES)
    uploaded = st.file_uploader("Upload resume PDF", type=["pdf"])
    manual_text = st.text_area("Or paste resume text", value=user.get("resume_text", ""), height=180)

    if st.button("Analyze Resume", type="primary"):
        text = manual_text
        if uploaded:
            text = extract_pdf_text(uploaded)
        if not text:
            st.error("Please upload a readable PDF or paste resume text.")
            return
        result = score_resume(text, target_company, user.get("skills", ""))
        prompt = f"Analyze this resume for {target_company}. Resume:\n{text[:4000]}\nResult:{result}"
        fallback = "\n".join([f"- {item}" for item in result["improvements"]])
        result["ai_feedback"] = ai.generate(prompt, fallback=f"### Section-wise Improvements\n{fallback}")
        db.update_user_profile(
            user["id"],
            user["name"],
            user.get("branch", ""),
            user.get("year", ""),
            __import__("json").loads(user.get("target_companies") or "[]"),
            user.get("skills", ""),
            text,
        )
        db.save_resume_result(user["id"], result)
        st.session_state["user"] = db.get_user(user["id"])
        st.success("Resume analysis saved.")
        show_result(result)


def show_result(result):
    c1, c2, c3 = st.columns(3)
    c1.metric("ATS Score", f"{result['ats_score']}%")
    c2.metric("Skills Match", f"{result['skills_match']}%")
    c3.metric("Grammar Issues", result["grammar_issues"])
    st.progress(result["ats_score"] / 100)
    st.subheader("Missing Keywords")
    st.write(", ".join(result["missing_keywords"]) or "No major keyword gaps found.")
    st.subheader("Quality Review")
    st.write(f"Project quality: {result['project_quality']}")
    st.write(f"Experience quality: {result['experience_quality']}")
    st.write(f"Formatting: {result['formatting']}")
    st.subheader("AI Suggestions")
    st.markdown(result["ai_feedback"])
