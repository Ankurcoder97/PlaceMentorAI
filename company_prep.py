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
    fallback_questions = build_fallback_questions(company, question_type, count, difficulty, process)

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


def build_fallback_questions(company, question_type, count, difficulty, process):
    banks = {
        "Coding": [
            f"Given an integer array, return indices of two numbers that add to a target. Include brute force and hash map approaches. Expected: O(n).",
            f"Find the longest substring without repeating characters. Explain sliding window and edge cases.",
            f"Merge overlapping intervals and return the final non-overlapping list. Discuss sorting complexity.",
            f"Given a binary tree, print level order traversal. Explain queue-based BFS.",
            f"Find the number of islands in a grid. Explain DFS/BFS and visited marking.",
            f"Find the first missing positive integer in an unsorted array. Aim for O(n) time.",
            f"Detect a cycle in a linked list and explain slow-fast pointer logic.",
            f"Find maximum subarray sum using Kadane's algorithm and dry run it.",
            f"Given a sorted rotated array, search a target using modified binary search.",
            f"Solve climbing stairs and explain how it becomes a Fibonacci DP problem.",
            f"Implement LRU cache and explain why hash map plus doubly linked list is used.",
            f"Given meeting intervals, find the minimum number of rooms required.",
            f"Find top K frequent elements using heap or bucket approach.",
            f"Check if a string has balanced parentheses using stack.",
            f"Find shortest path in an unweighted graph using BFS.",
            f"Generate all subsets of an array using backtracking.",
            f"Find longest common subsequence using dynamic programming.",
            f"Reverse nodes of a linked list in groups of K.",
            f"Find median of two sorted arrays and discuss binary-search optimization.",
            f"Design a rate limiter and explain data structures needed.",
        ],
        "Technical": [
            f"Explain ACID properties in DBMS with a transaction example.",
            f"What is normalization? Compare 1NF, 2NF, and 3NF with a simple student table.",
            f"Difference between primary key, foreign key, unique key, and candidate key.",
            f"Explain process vs thread and where multithreading is useful.",
            f"What is deadlock? Explain the four necessary conditions and prevention methods.",
            f"Difference between TCP and UDP. Which would you use for video calls and why?",
            f"What happens when you type google.com in a browser?",
            f"Explain OOPs pillars with examples from one of your projects.",
            f"Difference between method overloading and method overriding.",
            f"Explain REST API methods: GET, POST, PUT, PATCH, DELETE.",
            f"What is indexing in databases? Why can indexes slow down writes?",
            f"Explain joins in SQL: inner, left, right, and full join.",
            f"What is caching? Where would you use it in a web app?",
            f"Explain authentication vs authorization.",
            f"What is time complexity? Compare O(n), O(log n), and O(n²).",
            f"Explain stack vs queue and give real use cases.",
            f"What is garbage collection and why does memory management matter?",
            f"Explain horizontal vs vertical scaling.",
            f"What is a race condition? How can it be avoided?",
            f"Explain your best project architecture and the tradeoffs you made.",
        ],
        "HR": [
            f"Tell me about yourself for a {company} interview.",
            f"Why do you want to join {company}?",
            f"Why should {company} hire you over other candidates?",
            f"Describe a project challenge and how you solved it using STAR format.",
            f"Tell me about a time you worked in a team and handled conflict.",
            f"What are your strengths and weaknesses?",
            f"Where do you see yourself in five years?",
            f"Tell me about a time you failed and what you learned.",
            f"How do your skills match the {company} hiring process: {process}?",
            f"Are you comfortable relocating or working in a fast-paced environment?",
            f"Explain a time when you learned a new technology quickly.",
            f"What motivates you to work in software/technology?",
            f"How do you manage deadlines during exams and projects?",
            f"What is your biggest achievement in college?",
            f"Why did you choose your branch?",
            f"How do you handle feedback?",
            f"Tell me about your leadership experience.",
            f"What do you know about {company}'s products or culture?",
            f"What salary expectations do you have as a fresher?",
            f"Do you have any questions for the interviewer?",
        ],
        "Aptitude": [
            "A number is increased by 20% and then decreased by 20%. Find the net percentage change.",
            "A shopkeeper sells an item at 15% profit. If CP is Rs. 800, find SP.",
            "A and B can finish work in 12 and 18 days. Find time taken together.",
            "A train covers 240 km in 4 hours. Convert its speed to m/s.",
            "The ratio of boys to girls is 5:3. If total students are 64, find boys.",
            "A bag has 4 red, 5 blue, and 3 green balls. Find probability of drawing blue.",
            "In how many ways can 3 students be selected from 10?",
            "Find HCF and LCM of 24 and 36.",
            "If simple interest on Rs. 5000 for 2 years is Rs. 800, find rate percent.",
            "A person walks 5 km north, then 12 km east. Find shortest distance from start.",
            "A pipe fills a tank in 6 hours and another empties it in 9 hours. Find net fill time.",
            "A mixture has milk and water in 7:3. If mixture is 50 liters, find water quantity.",
            "Find the next number: 3, 6, 12, 24, ?",
            "If marked price is Rs. 1200 and discount is 25%, find selling price.",
            "A man spends 70% of salary and saves Rs. 9000. Find salary.",
            "Average of five numbers is 28. If one number is removed, average becomes 25. Find removed number.",
            "Two dice are thrown. Find probability of getting sum 7.",
            "A boat goes 30 km downstream in 3 hours and upstream in 5 hours. Find speed of stream.",
            "If x:y = 2:5 and y:z = 3:4, find x:z.",
            "A clock gains 5 minutes every hour. How much will it gain in 6 hours?",
        ],
    }
    if question_type == "Mixed":
        source = []
        for key in ["Coding", "Technical", "Aptitude", "HR"]:
            source.extend([f"{key}: {item}" for item in banks[key][:5]])
    else:
        source = banks.get(question_type, banks["Technical"])

    questions = []
    while len(questions) < count:
        questions.extend(source)
    return [f"{i}. {question}" for i, question in enumerate(questions[:count], 1)]


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
