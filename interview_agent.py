import json

import streamlit as st

import database as db
from ai_service import ai, improve_answer


QUESTION_BANK = {
    "HR interview": ["Tell me about yourself.", "Why should we hire you?", "Describe a challenge you handled."],
    "Technical interview": ["Explain OOPs pillars.", "What is normalization?", "Explain process vs thread."],
    "DSA interview": ["How would you solve Two Sum?", "Explain binary search.", "When do you use BFS?"],
    "Project-based interview": ["Explain your best project.", "What challenges did you face?", "How would you scale it?"],
    "Company-specific interview": ["Why this company?", "How do your skills match this role?", "Tell me about a time you showed ownership."],
}


def render_mock_interview(user):
    st.title("AI Mock Interview")
    interview_type = st.selectbox("Interview type", list(QUESTION_BANK.keys()))
    company = st.selectbox("Company", ["General"] + db.COMPANIES)

    key = "mock_session"
    if st.button("Start New Interview", type="primary"):
        st.session_state[key] = {"type": interview_type, "company": company, "index": 0, "transcript": []}
        st.rerun()

    session = st.session_state.get(key)
    if not session:
        st.info("Start an interview to receive one question at a time.")
        return

    questions = QUESTION_BANK[session["type"]]
    if session["index"] < len(questions):
        question = questions[session["index"]]
        st.subheader(f"Question {session['index'] + 1}")
        st.write(question)
        answer = st.text_area("Your answer", key=f"ans-{session['index']}", height=160)
        if st.button("Submit Answer"):
            feedback = improve_answer(question, answer, f"Company: {session['company']}; Skills: {user.get('skills', '')}")
            session["transcript"].append({"question": question, "answer": answer, "feedback": feedback})
            session["index"] += 1
            st.session_state[key] = session
            st.rerun()
    else:
        st.success("Interview completed.")
        report = generate_report(session["transcript"])
        st.markdown(report["text"])
        if st.button("Save Interview Report"):
            db.save_mock_interview(user["id"], session["type"], session["company"], session["transcript"], report["scores"], report["text"])
            st.session_state.pop(key, None)
            st.success("Interview report saved.")
            st.rerun()

    if session["transcript"]:
        st.subheader("Feedback So Far")
        for item in session["transcript"]:
            with st.expander(item["question"]):
                st.write(item["answer"])
                st.markdown(item["feedback"])


def generate_report(transcript):
    avg_len = sum(len(t["answer"].split()) for t in transcript) / max(len(transcript), 1)
    communication = min(90, 50 + int(avg_len))
    technical = 72 if any("technical" in t["question"].lower() or "solve" in t["question"].lower() for t in transcript) else 65
    confidence = 75 if avg_len > 25 else 58
    overall = int((communication + technical + confidence) / 3)
    text = f"""
### Final Interview Report
- Communication score: {communication}/100
- Technical score: {technical}/100
- Confidence score: {confidence}/100
- Overall score: {overall}/100

### Improvement Areas
- Add specific project examples.
- Use STAR format for HR answers.
- Speak in structured points instead of long paragraphs.
- Mention time and space complexity for DSA answers.

### Best Corrected Answer Pattern
Start with a one-line answer, add a concrete example, explain your role, and close with measurable impact.
"""
    return {"scores": {"communication": communication, "technical": technical, "confidence": confidence, "overall": overall}, "text": text}
