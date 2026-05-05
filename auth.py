import json

import sqlite3
import streamlit as st

import database as db


def render_auth():
    st.markdown(
        """
        <div class="pn-hero">
            <div class="pn-kicker">prepNinja presents</div>
            <div class="pn-title">PlaceMentor <span>AI</span></div>
            <div class="pn-subtitle">
                A dark, focused placement dojo for resumes, company prep, coding practice,
                aptitude, mock interviews, and readiness tracking.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab_login, tab_signup = st.tabs(["Login", "Signup"])

    with tab_login:
        email = st.text_input("Email", value="student@placementor.ai")
        password = st.text_input("Password", type="password", value="student123")
        if st.button("Login", type="primary"):
            user = db.get_user_by_email(email)
            if user and db.verify_password(password, user["password_hash"]):
                st.session_state["user"] = user
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid email or password.")
        st.info("Demo student: student@placementor.ai / student123\n\nAdmin: admin@placementor.ai / admin123")

    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Full name")
            signup_email = st.text_input("Signup email")
            signup_password = st.text_input("Create password", type="password")
            branch = st.text_input("Branch", value="Computer Science")
            year = st.selectbox("Year", ["First Year", "Second Year", "Third Year", "Final Year"])
            targets = st.multiselect("Target companies", db.COMPANIES, default=["TCS", "Accenture"])
            skills = st.text_input("Skills", value="Python, SQL, DSA")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                try:
                    db.create_user(name, signup_email, signup_password, branch, year, targets, skills)
                    st.success("Account created. Please login.")
                except sqlite3.IntegrityError:
                    st.error("Email already exists.")


def require_user():
    return st.session_state.get("user")


def logout():
    st.session_state.pop("user", None)
    st.rerun()


def render_profile(user):
    st.subheader("Student Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=user.get("name", ""))
        branch = st.text_input("Branch", value=user.get("branch", ""))
        year = st.selectbox("Year", ["First Year", "Second Year", "Third Year", "Final Year"], index=max(0, ["First Year", "Second Year", "Third Year", "Final Year"].index(user.get("year", "Final Year")) if user.get("year", "Final Year") in ["First Year", "Second Year", "Third Year", "Final Year"] else 3))
        targets = st.multiselect("Target companies", db.COMPANIES, default=json.loads(user.get("target_companies") or "[]"))
        skills = st.text_area("Skills", value=user.get("skills", ""))
        resume_text = st.text_area("Saved resume text", value=user.get("resume_text", ""), height=120)
        if st.form_submit_button("Update Profile"):
            db.update_user_profile(user["id"], name, branch, year, targets, skills, resume_text)
            st.session_state["user"] = db.get_user(user["id"])
            st.success("Profile updated.")
            st.rerun()
