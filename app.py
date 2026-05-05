import json
from pathlib import Path

import streamlit as st

import auth
import database as db
from ai_service import generate_hr_answer, generate_project_explanation
from aptitude import render_aptitude
from coding_platform import render_coding_platform
from company_prep import render_company_prep
from core_subjects import render_core_subjects
from dashboard import render_dashboard, render_progress, render_roadmap
from interview_agent import render_mock_interview
from resume_analyzer import render_resume_analyzer


st.set_page_config(page_title="prepNinja | PlaceMentor AI", page_icon="PN", layout="wide", initial_sidebar_state="expanded")


def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --pn-bg: #050816;
            --pn-panel: rgba(15, 23, 42, 0.86);
            --pn-card: rgba(17, 24, 39, 0.92);
            --pn-border: rgba(148, 163, 184, 0.18);
            --pn-primary: #38bdf8;
            --pn-accent: #f97316;
            --pn-green: #22c55e;
            --pn-text: #e5e7eb;
            --pn-muted: #94a3b8;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 12% 8%, rgba(56, 189, 248, 0.18), transparent 28%),
                radial-gradient(circle at 85% 10%, rgba(249, 115, 22, 0.14), transparent 24%),
                linear-gradient(135deg, #050816 0%, #0f172a 52%, #111827 100%);
            color: var(--pn-text);
        }
        div[data-testid="stToolbar"],
        div[data-testid="stActionButton"],
        div[data-testid="stDeployButton"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 2.75rem !important;
            pointer-events: auto !important;
            z-index: 999998 !important;
        }
        header[data-testid="stHeader"] [data-testid="stToolbar"],
        header[data-testid="stHeader"] [data-testid="stDeployButton"],
        header[data-testid="stHeader"] [data-testid="stActionButton"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
        header[data-testid="stHeader"] button,
        header[data-testid="stHeader"] [role="button"],
        button[data-testid="baseButton-headerNoPadding"],
        button[kind="headerNoPadding"],
        button[kind="header"] {
            visibility: visible !important;
            display: inline-flex !important;
            pointer-events: auto !important;
            opacity: 1 !important;
            color: #f8fafc !important;
            background: rgba(2, 6, 23, 0.82) !important;
            border: 1px solid rgba(56, 189, 248, 0.35) !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
        }
        header[data-testid="stHeader"] svg,
        button[kind="headerNoPadding"] svg,
        button[kind="header"] svg {
            color: #f8fafc !important;
            fill: #f8fafc !important;
            stroke: #f8fafc !important;
        }
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        button[aria-label*="sidebar" i],
        button[title*="sidebar" i] {
            visibility: visible !important;
            display: inline-flex !important;
            pointer-events: auto !important;
            opacity: 1 !important;
            z-index: 999999 !important;
            color: #f8fafc !important;
            background: rgba(2, 6, 23, 0.88) !important;
            border: 1px solid rgba(56, 189, 248, 0.45) !important;
            border-radius: 999px !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.32) !important;
        }
        [data-testid="collapsedControl"] *,
        [data-testid="stSidebarCollapsedControl"] *,
        button[aria-label*="sidebar" i] *,
        button[title*="sidebar" i] * {
            color: #f8fafc !important;
            fill: #f8fafc !important;
            stroke: #f8fafc !important;
            opacity: 1 !important;
        }
        .main .block-container {padding-top: 1.4rem; max-width: 1240px;}
        h1, h2, h3, h4, h5, h6, p, label, span, div {color: var(--pn-text);}
        [data-testid="stMarkdownContainer"] p {color: #cbd5e1;}
        .metric-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(8, 47, 73, 0.84));
            border: 1px solid var(--pn-border);
            border-radius: 22px;
            padding: 18px;
            box-shadow: 0 22px 55px rgba(0, 0, 0, 0.30);
        }
        .metric-label {font-size: 0.85rem; color: var(--pn-muted); font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase;}
        .metric-value {font-size: 2rem; font-weight: 900; line-height: 1.1;}
        .metric-help {font-size: 0.75rem; color: #93c5fd;}
        .pn-hero {
            background:
                linear-gradient(135deg, rgba(8, 47, 73, 0.92), rgba(15, 23, 42, 0.96)),
                radial-gradient(circle at top right, rgba(249, 115, 22, 0.28), transparent 35%);
            border: 1px solid var(--pn-border);
            border-radius: 30px;
            padding: 26px;
            margin-bottom: 22px;
            box-shadow: 0 26px 70px rgba(0, 0, 0, 0.34);
        }
        .pn-kicker {
            color: var(--pn-primary);
            font-weight: 900;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-size: 0.78rem;
            margin-bottom: 8px;
        }
        .pn-title {
            font-size: clamp(2rem, 5vw, 4rem);
            line-height: 0.95;
            font-weight: 950;
            letter-spacing: -0.06em;
            margin-bottom: 12px;
            color: #f8fafc;
        }
        .pn-title span {color: var(--pn-accent);}
        .pn-subtitle {
            max-width: 720px;
            color: #cbd5e1;
            font-size: 1.02rem;
            line-height: 1.65;
        }
        .pn-logo-placeholder {
            min-height: 190px;
            border: 1.5px dashed rgba(56, 189, 248, 0.55);
            border-radius: 26px;
            background: linear-gradient(145deg, rgba(2, 6, 23, 0.62), rgba(15, 23, 42, 0.78));
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #93c5fd;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .pn-logo-card,
        .pn-dashboard-logo-wrap {
            min-height: 210px;
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 26px;
            background: linear-gradient(145deg, rgba(2, 6, 23, 0.72), rgba(15, 23, 42, 0.82));
            padding: 18px;
            overflow: hidden;
            box-shadow: 0 24px 58px rgba(0, 0, 0, 0.32);
        }
        .pn-dashboard-logo-wrap {
            margin-top: 0;
            height: 234px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .pn-logo-card img {
            border-radius: 20px;
            object-fit: contain;
            max-height: 230px;
        }
        .pn-dashboard-logo-wrap [data-testid="stImage"],
        .pn-dashboard-logo-wrap [data-testid="stImage"] > img,
        .pn-dashboard-logo-wrap img,
        .pn-dashboard-logo {
            border-radius: 18px !important;
            max-height: 200px;
            width: 100%;
            object-fit: contain;
        }
        .pn-sidebar-logo img {
            border-radius: 18px;
            margin-bottom: 0.5rem;
            border: 1px solid rgba(56, 189, 248, 0.26);
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.24);
        }
        .pn-panel {
            background: var(--pn-panel);
            border: 1px solid var(--pn-border);
            border-radius: 22px;
            padding: 18px;
        }
        .pn-static-sidebar {
            position: sticky;
            top: 1rem;
            min-height: calc(100vh - 3rem);
            background:
                radial-gradient(circle at 30% 0%, rgba(56, 189, 248, 0.22), transparent 26%),
                linear-gradient(180deg, #020617 0%, #0f172a 54%, #111827 100%);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 26px;
            padding: 18px 16px;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
        }
        .pn-static-logo {
            width: 100%;
            border-radius: 18px;
            border: 1px solid rgba(56, 189, 248, 0.20);
            margin-bottom: 1.25rem;
            background: white;
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.28);
        }
        .pn-static-sidebar-title {
            font-size: 1.6rem;
            font-weight: 950;
            color: #f8fafc;
            margin-top: 0.75rem;
            margin-bottom: 0.2rem;
        }
        .pn-static-sidebar-subtitle {
            color: #93c5fd;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }
        .pn-static-nav-label {
            color: #cbd5e1;
            font-size: 0.82rem;
            font-weight: 800;
            margin: 1.2rem 0 0.55rem;
        }
        .pn-static-nav {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }
        .pn-nav-item {
            display: flex;
            align-items: center;
            gap: 0.62rem;
            padding: 0.45rem 0.55rem;
            border-radius: 12px;
            color: #dbeafe !important;
            text-decoration: none !important;
            font-weight: 700;
            font-size: 0.92rem;
            transition: all 140ms ease;
        }
        .pn-nav-item span {
            width: 0.82rem;
            height: 0.82rem;
            border-radius: 999px;
            background: #f8fafc;
            border: 2px solid rgba(255, 255, 255, 0.86);
        }
        .pn-nav-item:hover {
            background: rgba(56, 189, 248, 0.13);
            color: #ffffff !important;
            transform: translateX(2px);
        }
        .pn-nav-item.active {
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.22), rgba(249, 115, 22, 0.16));
            color: #ffffff !important;
        }
        .pn-nav-item.active span {
            background: #ff4b4b;
            border-color: #ffb4b4;
        }
        .pn-logout-link {
            display: inline-flex;
            margin-top: 1.1rem;
            padding: 0.65rem 0.9rem;
            border-radius: 14px;
            background: linear-gradient(135deg, #38bdf8, #f97316);
            color: #ffffff !important;
            text-decoration: none !important;
            font-weight: 900;
            box-shadow: 0 16px 34px rgba(14, 165, 233, 0.20);
        }
        section[data-testid="stSidebar"],
        div[data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            background:
                radial-gradient(circle at 30% 0%, rgba(56, 189, 248, 0.22), transparent 26%),
                linear-gradient(180deg, #020617 0%, #0f172a 54%, #111827 100%) !important;
            border-right: 1px solid rgba(148, 163, 184, 0.16);
            visibility: visible !important;
            opacity: 1 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc !important;
            opacity: 1 !important;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #dbeafe !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label {
            background: transparent !important;
            border-radius: 12px;
            padding: 4px 8px;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(56, 189, 248, 0.12) !important;
        }
        section[data-testid="stSidebar"] button[kind="header"] {
            background: #020617 !important;
            color: #f8fafc !important;
        }
        .stButton>button {
            border-radius: 14px;
            font-weight: 700;
            border: 1px solid rgba(56, 189, 248, 0.35);
            background: linear-gradient(135deg, #0ea5e9, #f97316);
            color: white;
            box-shadow: 0 14px 32px rgba(14, 165, 233, 0.22);
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] div,
        [data-testid="stMultiSelect"] div {
            background-color: rgba(15, 23, 42, 0.86);
            color: #f8fafc;
            border-color: rgba(148, 163, 184, 0.22);
        }
        [data-testid="stTabs"] button {
            color: #cbd5e1;
        }
        div[data-testid="stAlert"] {
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.18);
        }
        pre,
        code,
        .stCode,
        div[data-testid="stCodeBlock"],
        div[data-testid="stCodeBlock"] pre,
        div[data-testid="stCodeBlock"] code {
            background: #020617 !important;
            color: #e5e7eb !important;
            border: 1px solid rgba(56, 189, 248, 0.24) !important;
            border-radius: 16px !important;
        }
        div[data-testid="stCodeBlock"] {
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.26);
        }
        div[data-testid="stCodeBlock"] span,
        pre span,
        code span {
            color: #e5e7eb !important;
        }
        div[data-baseweb="select"] > div {
            background-color: rgba(15, 23, 42, 0.94) !important;
            border-color: rgba(56, 189, 248, 0.30) !important;
            color: #f8fafc !important;
        }
        div[data-baseweb="popover"] {
            background-color: #020617 !important;
        }
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {
            background-color: #020617 !important;
            color: #f8fafc !important;
        }
        div[data-baseweb="menu"] {
            background-color: #020617 !important;
            border: 1px solid rgba(56, 189, 248, 0.22) !important;
        }
        div[data-baseweb="menu"] ul,
        div[data-baseweb="menu"] li,
        ul[role="listbox"],
        li[role="option"] {
            background-color: #020617 !important;
            color: #f8fafc !important;
        }
        div[role="option"] {
            background-color: #020617 !important;
            color: #f8fafc !important;
        }
        div[role="option"] *,
        li[role="option"] *,
        ul[role="listbox"] * {
            color: #f8fafc !important;
            opacity: 1 !important;
        }
        div[role="option"]:hover {
            background-color: rgba(56, 189, 248, 0.16) !important;
        }
        div[aria-selected="true"],
        li[aria-selected="true"] {
            background-color: rgba(56, 189, 248, 0.22) !important;
            color: #ffffff !important;
        }
        div[data-baseweb="select"] svg {
            color: #93c5fd !important;
            fill: #93c5fd !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    db.init_db()
    inject_css()
    user = auth.require_user()
    if not user:
        auth.render_auth()
        return

    user = db.get_user(user["id"])
    st.session_state["user"] = user
    nav_col, content_col = st.columns([0.22, 0.78], gap="large")

    with nav_col:
        page = render_static_sidebar(user)

    with content_col:
        if page == "Dashboard":
            render_dashboard(user)
        elif page == "Profile":
            auth.render_profile(user)
        elif page == "Resume Analyzer":
            render_resume_analyzer(user)
        elif page == "Company Prep":
            render_company_prep(user)
        elif page == "Coding Platform":
            render_coding_platform(user)
        elif page == "Core Subjects":
            render_core_subjects(user)
        elif page == "AI Mock Interview":
            render_mock_interview(user)
        elif page == "Aptitude Practice":
            render_aptitude(user)
        elif page == "Project Trainer":
            render_project_trainer(user)
        elif page == "HR Trainer":
            render_hr_trainer(user)
        elif page == "Roadmap":
            render_roadmap(user)
        elif page == "Progress":
            render_progress(user)
        elif page == "Admin Panel":
            render_admin(user)


def render_static_sidebar(user):
    pages = [
        "Dashboard",
        "Profile",
        "Resume Analyzer",
        "Company Prep",
        "Coding Platform",
        "Core Subjects",
        "AI Mock Interview",
        "Aptitude Practice",
        "Project Trainer",
        "HR Trainer",
        "Roadmap",
        "Progress",
        "Admin Panel",
    ]
    with st.container(border=True):
        logo_path = Path("logo.jpeg")
        if logo_path.exists():
            st.image(str(logo_path), width="stretch")
        st.markdown(
            f"""
            <div class="pn-static-sidebar-title">prepNinja</div>
            <div class="pn-static-sidebar-subtitle">PlaceMentor AI</div>
            <div class="pn-static-sidebar-subtitle">{user['name']} | {user['role'].title()}</div>
            """,
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", pages, key="main_navigation")
        if st.button("Logout", key="static_logout"):
            auth.logout()
    return page


def render_project_trainer(user):
    st.title("Project Explanation Trainer")
    details = st.text_area("Enter project details", height=220, placeholder="Problem statement, tech stack, features, your role, challenges, results...")
    if st.button("Generate Project Explanation", type="primary"):
        if not details.strip():
            st.error("Please enter project details.")
        else:
            st.markdown(generate_project_explanation(details))


def render_hr_trainer(user):
    st.title("English and HR Communication Trainer")
    prompt_name = st.selectbox(
        "Question",
        [
            "Self-introduction",
            "Why should we hire you?",
            "Strengths and weaknesses",
            "Tell me about yourself",
            "Why this company?",
            "Where do you see yourself in 5 years?",
        ],
    )
    answer = st.text_area("Your draft answer", height=160)
    if st.button("Improve Answer", type="primary"):
        profile = {"branch": user.get("branch", ""), "skills": user.get("skills", ""), "year": user.get("year", "")}
        st.markdown(generate_hr_answer(prompt_name, answer, profile))


def render_admin(user):
    st.title("Admin Panel")
    if user.get("role") != "admin":
        st.error("Admin access required.")
        return

    tab1, tab2, tab3 = st.tabs(["Add Coding Question", "Students Progress", "Company Content"])
    with tab1:
        with st.form("add_coding"):
            title = st.text_input("Title")
            topic = st.selectbox("Topic", ["Array", "String", "Linked List", "Stack", "Queue", "Tree", "Graph", "DP", "Greedy", "Recursion", "Backtracking", "Binary Search"])
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            statement = st.text_area("Statement")
            sample_input = st.text_input("Sample input")
            sample_output = st.text_input("Sample output")
            approach = st.text_area("Expected approach")
            if st.form_submit_button("Add Question"):
                db.add_coding_question(title, topic, difficulty, statement, sample_input, sample_output, approach)
                st.success("Coding question added.")

    with tab2:
        users = db.list_users()
        st.dataframe(users, use_container_width=True)
        selected = st.selectbox("View progress for user id", [u["id"] for u in users])
        st.json(db.metrics_for_user(selected))

    with tab3:
        st.info("Company details are generated through AI and saved per student in this demo version.")
        st.dataframe(db.get_company_prep(user["id"]), use_container_width=True)


if __name__ == "__main__":
    main()
