import json
import re

import streamlit as st

import database as db
from ai_service import ai


FORMULAS = {
    "Number system": "Divisibility, HCF/LCM, remainders, unit digit cycles.",
    "Percentage": "Percentage = value / total * 100; change% = change / original * 100.",
    "Profit and loss": "Profit% = profit / CP * 100; Loss% = loss / CP * 100.",
    "Time and work": "Work = rate * time; combined rate = sum of individual rates.",
    "Time, speed, distance": "Distance = speed * time; convert km/h to m/s by multiplying 5/18.",
    "Ratio and proportion": "Use equivalent ratios and cross multiplication.",
    "Probability": "Probability = favourable outcomes / total outcomes.",
    "Permutation and combination": "nPr = n!/(n-r)!; nCr = n!/(r!(n-r)!).",
    "Logical reasoning": "Track conditions carefully using tables or diagrams.",
    "Verbal ability": "Focus on grammar, vocabulary, inference, and concise reading.",
}


def render_aptitude(user):
    st.title("Aptitude Practice")
    topic = st.selectbox("Topic", db.APTITUDE_TOPICS)
    c1, c2 = st.columns(2)
    difficulty = c1.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    count = c2.slider("Number of GPT questions", min_value=3, max_value=10, value=5)

    st.info(FORMULAS[topic])
    st.caption("Generate real placement-style mathematical problems, solve them, and get explanations.")

    session_key = f"aptitude_questions_{topic}_{difficulty}_{count}"
    if st.button("Generate GPT Aptitude Questions", type="primary"):
        st.session_state[session_key] = generate_aptitude_questions(topic, difficulty, count)
        st.rerun()

    questions = st.session_state.get(session_key)
    if not questions:
        st.warning("Click Generate GPT Aptitude Questions to create a fresh math quiz.")
        return

    score = 0
    answers = []
    with st.form("aptitude_quiz"):
        for i, q in enumerate(questions, 1):
            st.markdown(f"**{i}. {q['question']}**")
            choice = st.radio("Choose answer", q["options"], key=f"apt-{session_key}-{i}", label_visibility="collapsed")
            answers.append((q, choice))
        submitted = st.form_submit_button("Submit Quiz")

    if submitted:
        for q, choice in answers:
            if choice == q["answer"]:
                score += 1
        db.save_aptitude_score(user["id"], topic, score, len(questions))
        st.success(f"Score saved: {score}/{len(questions)}")

        st.subheader("Answer Review")
        for i, (q, choice) in enumerate(answers, 1):
            correct = choice == q["answer"]
            if correct:
                st.success(f"{i}. Correct: {q['answer']}")
            else:
                st.error(f"{i}. Your answer: {choice} | Correct answer: {q['answer']}")
            st.markdown(q["explanation"])


def generate_aptitude_questions(topic, difficulty, count):
    fallback_questions = fallback_math_questions(topic, difficulty, count)
    prompt = f"""
Generate {count} original placement aptitude MCQ problems for engineering campus placements.
Topic: {topic}
Difficulty: {difficulty}

Rules:
- Questions must be real mathematical/numerical problems, not theory questions.
- Each question must have exactly 4 options.
- Include the correct answer exactly matching one option.
- Include a short step-by-step explanation.
- Return only valid JSON, no markdown.

JSON format:
[
  {{
    "question": "A shopkeeper buys...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "B) ...",
    "explanation": "Step 1: ... Step 2: ..."
  }}
]
"""
    response = ai.generate(prompt, fallback=json.dumps(fallback_questions))
    parsed = parse_questions(response)
    return parsed if parsed else fallback_questions


def parse_questions(response):
    try:
        return validate_questions(json.loads(response))
    except Exception:
        match = re.search(r"\[[\s\S]*\]", response)
        if not match:
            return []
        try:
            return validate_questions(json.loads(match.group(0)))
        except Exception:
            return []


def validate_questions(items):
    valid = []
    for item in items:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        options = item.get("options", [])
        answer = str(item.get("answer", "")).strip()
        explanation = str(item.get("explanation", "")).strip()
        if question and isinstance(options, list) and len(options) == 4 and answer in options:
            valid.append(
                {
                    "question": question,
                    "options": [str(option) for option in options],
                    "answer": answer,
                    "explanation": explanation or "Review the formula and solve step by step.",
                }
            )
    return valid


def fallback_math_questions(topic, difficulty, count):
    bank = {
        "Percentage": [
            {
                "question": "A student's marks increased from 480 to 600. What is the percentage increase?",
                "options": ["A) 20%", "B) 25%", "C) 30%", "D) 15%"],
                "answer": "B) 25%",
                "explanation": "Increase = 600 - 480 = 120. Percentage increase = 120/480 * 100 = 25%.",
            },
            {
                "question": "If 35% of a number is 140, what is the number?",
                "options": ["A) 300", "B) 350", "C) 400", "D) 450"],
                "answer": "C) 400",
                "explanation": "Let the number be x. 35% of x = 140, so x = 140 * 100 / 35 = 400.",
            },
        ],
        "Profit and loss": [
            {
                "question": "A laptop is bought for Rs. 40,000 and sold at 15% profit. Find the selling price.",
                "options": ["A) Rs. 44,000", "B) Rs. 45,000", "C) Rs. 46,000", "D) Rs. 48,000"],
                "answer": "C) Rs. 46,000",
                "explanation": "Profit = 15% of 40,000 = 6,000. Selling price = 40,000 + 6,000 = 46,000.",
            },
            {
                "question": "An article sold for Rs. 720 gives a loss of 10%. What was its cost price?",
                "options": ["A) Rs. 760", "B) Rs. 780", "C) Rs. 800", "D) Rs. 820"],
                "answer": "C) Rs. 800",
                "explanation": "SP = 90% of CP. CP = 720 * 100 / 90 = 800.",
            },
        ],
        "Time and work": [
            {
                "question": "A can complete a work in 12 days and B in 18 days. How many days will they take together?",
                "options": ["A) 6.2 days", "B) 7.2 days", "C) 8 days", "D) 9 days"],
                "answer": "B) 7.2 days",
                "explanation": "Combined rate = 1/12 + 1/18 = 5/36. Time = 36/5 = 7.2 days.",
            },
            {
                "question": "If 8 workers finish a job in 15 days, how many days will 12 workers take?",
                "options": ["A) 8 days", "B) 10 days", "C) 12 days", "D) 14 days"],
                "answer": "B) 10 days",
                "explanation": "Workers * days is constant. 8 * 15 = 12 * x, so x = 10 days.",
            },
        ],
        "Time, speed, distance": [
            {
                "question": "A train travels 180 km in 3 hours. What is its speed in m/s?",
                "options": ["A) 12 m/s", "B) 15 m/s", "C) 16.67 m/s", "D) 20 m/s"],
                "answer": "C) 16.67 m/s",
                "explanation": "Speed = 180/3 = 60 km/h. Convert to m/s: 60 * 5/18 = 16.67 m/s.",
            },
            {
                "question": "A car covers 150 km at 50 km/h. How much time does it take?",
                "options": ["A) 2 hours", "B) 2.5 hours", "C) 3 hours", "D) 3.5 hours"],
                "answer": "C) 3 hours",
                "explanation": "Time = distance / speed = 150 / 50 = 3 hours.",
            },
        ],
        "Ratio and proportion": [
            {
                "question": "The ratio of boys to girls is 3:2. If there are 45 boys, how many girls are there?",
                "options": ["A) 20", "B) 25", "C) 30", "D) 35"],
                "answer": "C) 30",
                "explanation": "3 parts = 45, so 1 part = 15. Girls = 2 parts = 30.",
            },
            {
                "question": "Divide Rs. 840 in the ratio 2:3:7. What is the largest share?",
                "options": ["A) Rs. 420", "B) Rs. 450", "C) Rs. 480", "D) Rs. 490"],
                "answer": "D) Rs. 490",
                "explanation": "Total parts = 12. One part = 840/12 = 70. Largest share = 7 * 70 = 490.",
            },
        ],
        "Probability": [
            {
                "question": "One card is drawn from a standard deck. What is the probability of drawing a king?",
                "options": ["A) 1/13", "B) 1/26", "C) 1/4", "D) 4/13"],
                "answer": "A) 1/13",
                "explanation": "There are 4 kings in 52 cards. Probability = 4/52 = 1/13.",
            },
            {
                "question": "A dice is rolled once. What is the probability of getting an even number?",
                "options": ["A) 1/6", "B) 1/3", "C) 1/2", "D) 2/3"],
                "answer": "C) 1/2",
                "explanation": "Even outcomes are 2, 4, 6. Probability = 3/6 = 1/2.",
            },
        ],
        "Permutation and combination": [
            {
                "question": "In how many ways can 3 students be selected from 8 students?",
                "options": ["A) 24", "B) 48", "C) 56", "D) 64"],
                "answer": "C) 56",
                "explanation": "Use combination: 8C3 = 8*7*6 / 3*2*1 = 56.",
            },
            {
                "question": "How many 3-letter arrangements can be made from A, B, C, D without repetition?",
                "options": ["A) 12", "B) 18", "C) 24", "D) 36"],
                "answer": "C) 24",
                "explanation": "Use permutation: 4P3 = 4*3*2 = 24.",
            },
        ],
    }
    default = [
        {
            "question": "Find the HCF of 36 and 60.",
            "options": ["A) 6", "B) 9", "C) 12", "D) 18"],
            "answer": "C) 12",
            "explanation": "Factors common to 36 and 60 include 1, 2, 3, 4, 6, 12. Highest is 12.",
        },
        {
            "question": "What is the remainder when 47 is divided by 5?",
            "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
            "answer": "B) 2",
            "explanation": "47 = 5 * 9 + 2, so the remainder is 2.",
        },
    ]
    questions = bank.get(topic, default)
    expanded = []
    while len(expanded) < count:
        expanded.extend(questions)
    return expanded[:count]
