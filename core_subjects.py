import json
import re

import streamlit as st

import database as db
from ai_service import ai


TOPICS = {
    "DBMS": ["Keys and normalization", "Joins and SQL queries", "Transactions and ACID", "Indexing"],
    "Operating System": ["Process vs thread", "Deadlock", "CPU scheduling", "Memory management"],
    "Computer Networks": ["OSI and TCP/IP", "TCP vs UDP", "HTTP vs HTTPS", "DNS"],
    "OOPs": ["OOPs pillars", "Overloading vs overriding", "Abstract class vs interface", "Constructor"],
    "SQL": ["Joins", "GROUP BY and HAVING", "Subqueries", "Primary key vs foreign key"],
    "DSA": ["Arrays and hashing", "Stack and queue", "Trees", "Dynamic programming basics"],
    "Software Engineering": ["SDLC", "Agile vs waterfall", "Testing types", "Software maintenance"],
}


FALLBACK_QUESTIONS = {
    "DBMS": [
        ("What is normalization? Why is it used?", "Normalization organizes data to reduce redundancy and improve consistency. Common forms are 1NF, 2NF, 3NF, and BCNF."),
        ("What is the difference between primary key and foreign key?", "A primary key uniquely identifies a row. A foreign key links one table to another table's primary key."),
        ("Explain ACID properties.", "Atomicity, Consistency, Isolation, and Durability ensure reliable database transactions."),
        ("What is an index in DBMS?", "An index speeds up search queries but can slow insert/update operations because the index also needs updates."),
    ],
    "Operating System": [
        ("What is the difference between process and thread?", "A process is an independent program in execution. A thread is a lightweight unit inside a process sharing memory with other threads."),
        ("What is deadlock?", "Deadlock happens when processes wait forever for resources held by each other."),
        ("What are the necessary conditions for deadlock?", "Mutual exclusion, hold and wait, no preemption, and circular wait."),
        ("What is virtual memory?", "Virtual memory lets a system use disk space as an extension of RAM."),
    ],
    "Computer Networks": [
        ("What is the difference between TCP and UDP?", "TCP is reliable and connection-oriented. UDP is faster, connectionless, and does not guarantee delivery."),
        ("What happens when you type a URL in a browser?", "DNS resolves the domain, connection is made, HTTP/HTTPS request is sent, server responds, and browser renders the page."),
        ("What is DNS?", "DNS converts domain names like google.com into IP addresses."),
        ("What is the difference between HTTP and HTTPS?", "HTTPS is HTTP with encryption using TLS/SSL."),
    ],
    "OOPs": [
        ("Explain the four pillars of OOPs.", "Encapsulation, inheritance, polymorphism, and abstraction."),
        ("What is polymorphism?", "Polymorphism means one interface can have many forms, such as method overloading and overriding."),
        ("Difference between abstraction and encapsulation?", "Abstraction hides implementation details. Encapsulation binds data and methods together and controls access."),
        ("What is inheritance?", "Inheritance allows one class to reuse and extend another class's properties and behavior."),
    ],
    "SQL": [
        ("Difference between WHERE and HAVING?", "WHERE filters rows before grouping. HAVING filters groups after GROUP BY."),
        ("What is an INNER JOIN?", "INNER JOIN returns rows where matching values exist in both tables."),
        ("What is GROUP BY?", "GROUP BY groups rows with the same values so aggregate functions can be applied."),
        ("Write a query to find duplicate emails.", "SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;"),
    ],
    "DSA": [
        ("Why is hashing used?", "Hashing gives fast average O(1) lookup, insert, and delete using a hash table."),
        ("Difference between stack and queue?", "Stack follows LIFO. Queue follows FIFO."),
        ("When do we use BFS?", "BFS is used for level-order traversal and shortest path in unweighted graphs."),
        ("What is dynamic programming?", "DP solves problems by storing results of overlapping subproblems."),
    ],
    "Software Engineering": [
        ("What is SDLC?", "SDLC is the software development life cycle: planning, analysis, design, implementation, testing, deployment, and maintenance."),
        ("Agile vs waterfall?", "Waterfall is sequential. Agile is iterative and supports frequent feedback."),
        ("What is unit testing?", "Unit testing checks small independent units of code, usually functions or classes."),
        ("What is software maintenance?", "Maintenance means fixing bugs, improving features, and adapting software after release."),
    ],
}


def render_core_subjects(user):
    st.title("Core Subject Interview Prep")
    st.caption("Simple, direct questions that are commonly asked in campus placement interviews.")

    subject = st.selectbox("Choose subject", db.SUBJECTS)
    topic = st.selectbox("Focus topic", TOPICS[subject])
    count = st.slider("Number of interview questions", min_value=3, max_value=10, value=5)

    key = f"core_questions_{subject}_{topic}_{count}"
    if st.button("Generate Interview Questions", type="primary"):
        st.session_state[key] = generate_interview_questions(subject, topic, count)
        st.rerun()

    questions = st.session_state.get(key) or generate_interview_questions(subject, topic, count, use_ai=False)

    st.subheader(f"{subject}: {topic}")
    st.info("Tip: answer in 4 parts: definition, example, use case, and one interview keyword.")

    for index, item in enumerate(questions, 1):
        with st.expander(f"Q{index}. {item['question']}", expanded=index == 1):
            st.markdown("**Simple model answer:**")
            st.write(item["answer"])
            if item.get("example"):
                st.markdown("**Example:**")
                st.write(item["example"])
            if item.get("keywords"):
                st.markdown("**Keywords to mention:**")
                st.write(", ".join(item["keywords"]))

            user_answer = st.text_area("Practice your answer", key=f"core-answer-{key}-{index}", height=110)
            c1, c2 = st.columns([1, 1])
            if c1.button("Check My Answer", key=f"check-core-{key}-{index}"):
                feedback = check_core_answer(subject, item["question"], item["answer"], user_answer)
                st.markdown(feedback)
            if c2.button("Mark Topic Done", key=f"done-core-{key}-{index}"):
                db.save_subject_progress(user["id"], subject, topic, 85, True)
                st.success("Progress saved for this topic.")


def generate_interview_questions(subject, topic, count, use_ai=True):
    fallback = fallback_questions(subject, topic, count)
    if not use_ai:
        return fallback

    prompt = f"""
Generate {count} interview questions actually asked in engineering campus placements.
Subject: {subject}
Focus topic: {topic}

Rules:
- Keep questions direct and realistic.
- Avoid long academic theory.
- Include simple model answer, practical example, and keywords.
- Return only valid JSON.

JSON format:
[
  {{
    "question": "What is normalization?",
    "answer": "Simple 3-5 line answer.",
    "example": "Short example.",
    "keywords": ["keyword1", "keyword2"]
  }}
]
"""
    response = ai.generate(prompt, fallback=json.dumps(fallback))
    parsed = parse_questions(response)
    return parsed if parsed else fallback


def fallback_questions(subject, topic, count):
    items = FALLBACK_QUESTIONS.get(subject, FALLBACK_QUESTIONS["DBMS"])
    formatted = []
    for question, answer in items:
        formatted.append(
            {
                "question": question,
                "answer": answer,
                "example": example_for(subject, question),
                "keywords": keywords_for(subject),
            }
        )
    while len(formatted) < count:
        formatted.extend(formatted)
    return formatted[:count]


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
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if not question or not answer:
            continue
        keywords = item.get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []
        valid.append(
            {
                "question": question,
                "answer": answer,
                "example": str(item.get("example", "")).strip(),
                "keywords": [str(k) for k in keywords[:6]],
            }
        )
    return valid


def check_core_answer(subject, question, model_answer, user_answer):
    fallback = f"""
### Feedback
Your answer should be short, clear, and interview-focused.

### Better Structure
1. Start with a definition.
2. Add one simple example.
3. Mention one important keyword.
4. End with why it is useful.

### Model Direction
{model_answer}
"""
    prompt = f"""
Evaluate this campus placement interview answer.
Subject: {subject}
Question: {question}
Model answer: {model_answer}
Student answer: {user_answer}

Give score out of 10, missing points, and a better answer.
"""
    return ai.generate(prompt, fallback=fallback)


def keywords_for(subject):
    return {
        "DBMS": ["ACID", "normalization", "keys", "joins"],
        "Operating System": ["process", "thread", "deadlock", "memory"],
        "Computer Networks": ["TCP/IP", "DNS", "HTTP", "reliability"],
        "OOPs": ["encapsulation", "inheritance", "polymorphism", "abstraction"],
        "SQL": ["JOIN", "GROUP BY", "HAVING", "subquery"],
        "DSA": ["time complexity", "space complexity", "hashing", "traversal"],
        "Software Engineering": ["SDLC", "Agile", "testing", "maintenance"],
    }.get(subject, [])


def example_for(subject, question):
    if subject == "DBMS":
        return "Example: A student_id can uniquely identify a student row in a Students table."
    if subject == "Operating System":
        return "Example: A browser is a process; each tab may use one or more threads."
    if subject == "Computer Networks":
        return "Example: Video calls often prefer UDP because speed matters more than perfect delivery."
    if subject == "OOPs":
        return "Example: A Shape reference can call draw() differently for Circle and Rectangle."
    if subject == "SQL":
        return "Example: GROUP BY department can calculate average salary per department."
    if subject == "DSA":
        return "Example: A hash map can solve Two Sum in O(n) time."
    return "Example: Agile teams deliver software in small iterations and collect feedback frequently."
