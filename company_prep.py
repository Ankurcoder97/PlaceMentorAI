import streamlit as st

import database as db
from ai_service import ai


COMPANY_META = {
    "TCS": ("Easy-Medium", "NQT, aptitude, coding, technical, HR"),
    "Infosys": ("Easy-Medium", "InfyTQ/aptitude, coding, technical, HR"),
    "Wipro": ("Easy-Medium", "Aptitude, essay, coding, technical, HR"),
    "Accenture": ("Medium", "Cognitive, technical MCQ, coding, communication, interview"),
    "Capgemini": ("Medium", "Aptitude, pseudo code, game-based, technical, HR"),
    "Cognizant": ("Medium", "Aptitude, coding, communication, technical, HR"),
    "Deloitte": ("Medium", "Aptitude, case/technical, managerial, HR"),
    "Amazon": ("Hard", "OA, DSA interviews, bar raiser, leadership principles"),
    "Microsoft": ("Hard", "OA, DSA, design fundamentals, technical loops"),
    "Google": ("Hard", "OA, algorithms, problem solving, googliness"),
    "Salesforce": ("Medium-Hard", "OA, technical, project, values, HR"),
}


def generate_company_plan(company, user, duration):
    difficulty, process = COMPANY_META[company]
    fallback = f"""
### {company} Overview
{company} values problem solving, clear communication, strong fundamentals, and project ownership.

### Hiring Process
{process}

### Expected Rounds
1. Online aptitude/coding assessment
2. Technical interview on DSA, projects, and CS fundamentals
3. HR/managerial interview

### Important Aptitude Topics
Percentages, profit and loss, time and work, speed-distance, probability, logical reasoning, verbal ability.

### Coding Topics
Arrays, strings, hashing, recursion, linked list, stack, queue, trees, graphs, DP basics.

### Core CS Topics
DBMS normalization/SQL, OOPs pillars, OS process/thread/deadlock, CN TCP/IP and HTTP.

### HR Questions
- Tell me about yourself.
- Why {company}?
- Describe a challenge you solved.
- What are your strengths and weaknesses?

### Technical Questions
- Explain your best project architecture.
- Difference between process and thread.
- Write SQL joins.
- Explain polymorphism with an example.

### {duration}-Day Preparation Plan
Spend 50% time on DSA and coding, 25% on core CS, 15% on aptitude, and 10% on HR/project explanation. Take a mock every 3 days.

### Previous-Style Questions
- Solve a two-pointer array problem.
- Write SQL query using GROUP BY.
- Explain your project with tradeoffs.
- Answer a situational HR question using STAR.

### Difficulty Level
{difficulty}

### Resume Tips
Highlight {company}-relevant keywords, quantified project outcomes, team collaboration, and role-ready skills.
"""
    prompt = f"Create a detailed placement plan for {company}, duration {duration} days, profile {user}."
    return ai.generate(prompt, fallback=fallback)


def generate_company_questions(company, question_type, count, user):
    difficulty, process = COMPANY_META[company]
    fallback_questions = []
    for i in range(1, count + 1):
        if question_type == "Coding":
            fallback_questions.append(
                f"{i}. {company} {difficulty} coding question: Solve an array/string problem using hashing or two pointers. Explain brute force, optimized approach, and complexity."
            )
        elif question_type == "Technical":
            fallback_questions.append(
                f"{i}. Explain one core CS concept for {company}: DBMS transaction, OOPs polymorphism, OS deadlock, or CN TCP/IP with a project example."
            )
        elif question_type == "HR":
            fallback_questions.append(
                f"{i}. Why do you want to join {company}, and how do your skills match its hiring process: {process}?"
            )
        elif question_type == "Aptitude":
            fallback_questions.append(
                f"{i}. Practice a {company}-style aptitude question from percentage, time-work, probability, logical reasoning, or verbal ability."
            )
        else:
            fallback_questions.append(
                f"{i}. Mixed {company} placement question covering aptitude, DSA, core CS, project explanation, and HR communication."
            )

    fallback = f"""
### GPT-Generated {company} {question_type} Questions
Difficulty: {difficulty}
Hiring process reference: {process}

{chr(10).join(fallback_questions)}

### How to Practice
- Attempt each answer before viewing hints.
- Speak technical answers aloud for 60 seconds.
- For coding questions, write code and submit it in the Coding Platform.
- Save weak topics in your roadmap.
"""
    prompt = f"""
Generate {count} fresh placement preparation questions for {company}.
Question type: {question_type}
Difficulty: {difficulty}
Hiring process: {process}
Student profile: {user}

For coding questions, include problem statement, input/output style, constraints, hints, expected approach, and complexity.
For HR/technical questions, include what interviewer expects and a model answer outline.
"""
    return ai.generate(prompt, fallback=fallback)


def render_company_prep(user):
    st.title("Company-Wise Preparation Agent")
    tab_plan, tab_questions = st.tabs(["AI Company Plan", "GPT Question Generator"])

    with tab_plan:
        company = st.selectbox("Choose company", db.COMPANIES, key="plan-company")
        duration = st.radio("Preparation duration", ["7", "15", "30"], horizontal=True)
        if st.button("Generate Company Plan", type="primary"):
            content = generate_company_plan(company, user, duration)
            db.save_company_prep(user["id"], company, content)
            st.success(f"{company} preparation plan generated.")
            st.markdown(content)

    with tab_questions:
        q_company = st.selectbox("Company for questions", db.COMPANIES, key="question-company")
        question_type = st.selectbox("Question type", ["Mixed", "Coding", "Technical", "HR", "Aptitude"])
        count = st.slider("Number of questions", min_value=3, max_value=20, value=10)
        if st.button("Generate GPT Questions for Company", type="primary"):
            content = generate_company_questions(q_company, question_type, count, user)
            db.save_company_prep(user["id"], q_company, content)
            st.success(f"{count} {question_type.lower()} questions generated for {q_company}.")
            st.markdown(content)

    st.subheader("Saved Company Plans")
    for item in db.get_company_prep(user["id"])[:5]:
        with st.expander(f"{item['company']} - {item['status']}"):
            st.markdown(item["content"])
