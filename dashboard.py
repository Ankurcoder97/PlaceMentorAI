import json
import base64
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db


def score_card(label, value, help_text=""):
    color = "#22c55e" if value >= 75 else "#f59e0b" if value >= 55 else "#ef4444"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{value}%</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(user):
    hero_left, hero_right = st.columns([2.25, 1])
    with hero_left:
        st.markdown(
            f"""
            <div class="pn-hero">
                <div class="pn-kicker">prepNinja placement dojo</div>
                <div class="pn-title">Welcome back, <span>{user['name'].split()[0]}</span></div>
                <div class="pn-subtitle">
                    Train smarter with AI-generated company questions, resume feedback,
                    coding submissions, aptitude drills, mock interviews, and readiness analytics.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        logo_path = Path("logo.jpeg")
        if logo_path.exists():
            st.markdown(render_logo_card(logo_path), unsafe_allow_html=True)
        else:
            st.markdown(
                """
                <div class="pn-logo-placeholder">
                    Add prepNinja<br>team logo here
                </div>
                """,
                unsafe_allow_html=True,
            )
    metrics = db.metrics_for_user(user["id"])

    cols = st.columns(5)
    with cols[0]:
        score_card("Readiness", metrics["readiness"], "Overall")
    with cols[1]:
        score_card("Resume", metrics["resume"], "ATS")
    with cols[2]:
        score_card("Coding", metrics["coding"], "Solved")
    with cols[3]:
        score_card("Core CS", metrics["core"], "Subjects")
    with cols[4]:
        score_card("Interview", metrics["interview"], "Mocks")

    st.subheader("Placement Readiness")
    st.progress(metrics["readiness"] / 100)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Weak Areas")
        for area in metrics["weak_areas"]:
            st.warning(area)
    with c2:
        st.subheader("Daily Preparation Tasks")
        for task in db.today_tasks(user):
            st.checkbox(task, key=f"daily-{task}")

    st.subheader("Progress Overview")
    df = pd.DataFrame(
        [
            {"Area": "Resume", "Score": metrics["resume"]},
            {"Area": "Coding", "Score": metrics["coding"]},
            {"Area": "Core CS", "Score": metrics["core"]},
            {"Area": "Interview", "Score": metrics["interview"]},
            {"Area": "Aptitude", "Score": metrics["aptitude"]},
        ]
    )
    fig = px.bar(df, x="Area", y="Score", color="Score", range_y=[0, 100], color_continuous_scale=["#38bdf8", "#22c55e", "#f97316"])
    style_dark_chart(fig)
    st.plotly_chart(fig, width="stretch")


def render_logo_card(logo_path):
    encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    return f"""
    <div class="pn-dashboard-logo-wrap">
        <img src="data:image/jpeg;base64,{encoded}" alt="prepNinja logo" class="pn-dashboard-logo" />
    </div>
    """


def style_dark_chart(fig):
    fig.update_layout(
        paper_bgcolor="rgba(2, 6, 23, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0.82)",
        font={"color": "#e5e7eb"},
        margin={"l": 24, "r": 24, "t": 28, "b": 24},
        coloraxis_colorbar={
            "tickfont": {"color": "#cbd5e1"},
            "title": {"font": {"color": "#cbd5e1"}},
        },
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.20)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.20)")
    return fig


def render_progress(user):
    st.title("Progress Tracker")
    metrics = db.metrics_for_user(user["id"])
    st.metric("Overall Readiness", f"{metrics['readiness']}%")

    resume = db.get_resume_history(user["id"])
    solved = db.get_solved_questions(user["id"])
    subjects = db.get_subject_progress(user["id"])
    aptitude = db.get_aptitude_scores(user["id"])
    interviews = db.get_mock_interviews(user["id"])
    company = db.get_company_prep(user["id"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Coding Solved", len(solved))
    c2.metric("Mock Interviews", len(interviews))
    c3.metric("Company Plans", len(company))

    if resume:
        df = pd.DataFrame(resume)
        st.subheader("Resume Score History")
        st.line_chart(df.set_index("created_at")["ats_score"])
    if solved:
        st.subheader("Solved Problems by Topic")
        st.bar_chart(pd.DataFrame(solved).groupby("topic").size())
    if subjects:
        st.subheader("Core Subject Scores")
        sdf = pd.DataFrame(subjects)
        fig = px.bar(sdf, x="subject", y="score", color="completed")
        style_dark_chart(fig)
        st.plotly_chart(fig, width="stretch")
    if aptitude:
        st.subheader("Aptitude Attempts")
        adf = pd.DataFrame(aptitude)
        adf["percent"] = adf["score"] / adf["total"] * 100
        fig = px.line(adf, x="created_at", y="percent", color="topic", markers=True)
        style_dark_chart(fig)
        st.plotly_chart(fig, width="stretch")
    if interviews:
        st.subheader("Mock Interview Scores")
        idf = pd.DataFrame(interviews)
        fig = px.bar(idf, x="created_at", y="overall_score", color="interview_type")
        style_dark_chart(fig)
        st.plotly_chart(fig, width="stretch")


def render_roadmap(user):
    st.title("Placement Roadmap Generator")
    metrics = db.metrics_for_user(user["id"])
    targets = json.loads(user.get("target_companies") or "[]")
    if st.button("Generate 7-Day Roadmap", type="primary"):
        tasks = []
        for i in range(1, 8):
            tasks.extend(
                [
                    {"date": str(date.today()), "category": "DSA", "task": f"Day {i}: Solve one {['Array','String','DP','Tree'][i % 4]} problem."},
                    {"date": str(date.today()), "category": "Core CS", "task": f"Day {i}: Revise {db.SUBJECTS[i % len(db.SUBJECTS)]} interview notes."},
                    {"date": str(date.today()), "category": "Company", "task": f"Day {i}: Prepare for {(targets or ['target company'])[0]} round expectations."},
                ]
            )
        db.add_roadmap_tasks(user["id"], tasks)
        st.success("Roadmap generated.")
        st.rerun()

    st.info(f"Roadmap priority: improve {', '.join(metrics['weak_areas'])}.")
    for task in db.get_roadmap_tasks(user["id"]):
        checked = st.checkbox(f"{task['category']}: {task['task']}", value=bool(task["completed"]), key=f"task-{task['id']}")
        if checked != bool(task["completed"]):
            db.toggle_task(task["id"], checked)
