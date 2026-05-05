import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import streamlit as st

import database as db
from ai_service import ai

TOPICS = ["All", "Array", "String", "Linked List", "Stack", "Queue", "Tree", "Graph", "DP", "Greedy", "Recursion", "Backtracking", "Binary Search"]


def render_coding_platform(user):
    st.title("Coding Preparation Platform")
    c1, c2 = st.columns(2)
    topic = c1.selectbox("Topic", TOPICS)
    difficulty = c2.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    questions = db.get_coding_questions(topic, difficulty)
    solved = {q["question_id"] for q in db.get_solved_questions(user["id"])}

    if not questions:
        st.info("No questions found for this filter.")
        return

    q_map = {f"{'Solved - ' if q['id'] in solved else ''}{q['title']} ({q['topic']} | {q['difficulty']})": q for q in questions}
    selected_label = st.selectbox("Problem", list(q_map.keys()))
    question = q_map[selected_label]

    render_leetcode_problem(question)

    language = st.selectbox("Language", ["Python", "Java", "C++", "JavaScript"])
    solution = st.text_area("Write your solution", height=260, placeholder="Paste your complete solution here...")

    with st.expander("Run Code Against Test Cases", expanded=True):
        st.caption("Python execution is supported locally with a 3-second timeout. For Java/C++/JavaScript, use AI review or paste expected output manually.")
        test_input = st.text_area("Test input", value=question["sample_input"] or "", height=90)
        expected_output = st.text_area("Expected output", value=question["sample_output"] or "", height=70)
        if st.button("Run Code"):
            if language != "Python":
                st.warning("Run Code currently supports Python only. You can still submit other languages for AI review.")
            elif not solution.strip():
                st.error("Please write Python code before running.")
            else:
                result = run_python_code(solution, test_input, expected_output)
                if result["passed"] is True:
                    st.success(f"Test passed in {result['time_ms']} ms")
                elif result["passed"] is False:
                    st.error(f"Test failed in {result['time_ms']} ms")
                else:
                    st.warning(f"Code ran in {result['time_ms']} ms")
                if result["stdout"]:
                    st.subheader("Output")
                    st.code(result["stdout"], language="text")
                if result["stderr"]:
                    st.subheader("Errors")
                    st.code(result["stderr"], language="text")
                if expected_output.strip():
                    st.subheader("Expected")
                    st.code(expected_output, language="text")

    b1, b2, b3, b4, b5 = st.columns(5)
    action = None
    if b1.button("Explain"):
        action = "Explain the problem"
    if b2.button("Hint"):
        action = "Give hints"
    if b3.button("Check Logic"):
        action = "Check logic"
    if b4.button("Find Bugs"):
        action = "Find bugs"
    if b5.button("Optimize"):
        action = "Suggest optimized approach and complexity"

    if action:
        fallback = f"### {action}\nUse this approach: {question['approach']}\n\nTime complexity depends on implementation; aim for the expected optimal pattern for {question['topic']}."
        st.markdown(ai.generate(f"{action} for coding problem {question}. User solution:\n{solution}", fallback=fallback))

    c_submit, c_solve = st.columns([1, 1])
    if c_submit.button("Submit Code for AI Review", type="primary"):
        if not solution.strip():
            st.error("Please write code before submitting.")
        else:
            review = review_code_submission(question, language, solution)
            db.save_code_submission(
                user["id"],
                question["id"],
                language,
                solution,
                review["score"],
                review["status"],
                review["feedback"],
            )
            st.success(f"Submission reviewed: {review['status']} ({review['score']}/100)")
            st.markdown(review["feedback"])
            if review["score"] >= 70:
                st.info("This question was automatically added to your solved list.")

    if c_solve.button("Mark as Solved Manually"):
        db.mark_question_solved(user["id"], question["id"], solution)
        st.success("Problem marked as solved.")
        st.rerun()

    submissions = db.get_code_submissions(user["id"], question["id"])
    if submissions:
        st.subheader("Submission History for This Problem")
        for sub in submissions[:5]:
            with st.expander(f"{sub['submitted_at']} - {sub['language']} - {sub['status']} - {sub['ai_score']}/100"):
                st.code(sub["code"], language=sub["language"].lower())
                st.markdown(sub["feedback"])

    st.subheader("Coding Progress")
    solved_rows = db.get_solved_questions(user["id"])
    st.metric("Solved Problems", f"{len(solved_rows)} / {len(db.get_coding_questions())}")
    if solved_rows:
        df = pd.DataFrame(solved_rows)
        st.bar_chart(df.groupby("topic").size())


def review_code_submission(question, language, code):
    score = heuristic_code_score(question, code)
    status = "Accepted by AI" if score >= 70 else "Needs Improvement"
    fallback = f"""
### AI Code Review
Status: {status}
Score: {score}/100

### Logic Review
Your solution was submitted successfully inside PlaceMentor AI. Compare it with the expected idea: {question['approach']}

### Optimization Advice
- State the brute-force approach first in interviews.
- Explain the optimized data structure or pattern.
- Mention time and space complexity clearly.
- Add edge cases such as empty input, duplicates, and boundary values.

### Expected Complexity
Use the standard optimal complexity for {question['topic']} problems.
"""
    prompt = f"""
Review this placement coding submission like an interviewer.
Return status, score out of 100, bugs, optimized approach, and time/space complexity.

Problem: {question}
Language: {language}
Code:
{code}
"""
    feedback = ai.generate(prompt, fallback=fallback)
    return {"score": score, "status": status, "feedback": feedback}


def render_leetcode_problem(question):
    st.subheader(question["title"])
    st.caption(f"{question['difficulty']} | {question['topic']} | Placement DSA")
    tab_description, tab_editorial, tab_hints = st.tabs(["Description", "Editorial", "Hints"])

    with tab_description:
        st.markdown(build_problem_description(question))

    with tab_editorial:
        key = f"editorial_{question['id']}"
        if key not in st.session_state:
            st.session_state[key] = build_editorial_fallback(question)
        if st.button("Generate Full GPT Editorial", key=f"gen-editorial-{question['id']}"):
            st.session_state[key] = explain_question_like_leetcode(question)
        st.markdown(st.session_state[key])

    with tab_hints:
        st.markdown(
            f"""
### Hint 1
Identify the pattern: **{question['topic']}**.

### Hint 2
Start with a brute-force idea, then ask what repeated work can be removed.

### Hint 3
Expected direction: {question['approach']}
"""
        )


def build_problem_description(question):
    return f"""
### Problem Statement
{question['statement']}

Write a function or complete program that solves the problem for the given input.

### Example 1
```text
Input:
{question['sample_input']}

Output:
{question['sample_output']}
```

### Explanation
The output is produced by applying the required {question['topic']} logic to the input. Your solution should handle the same pattern for hidden test cases.

### Constraints
- Input size can be large enough that inefficient brute force may fail.
- Values may include edge cases such as empty input, duplicates, sorted/unsorted order, or boundary values.
- Your solution should avoid unnecessary extra work.
- If no valid answer exists, handle it gracefully based on your chosen output convention.

### Follow Up
Can you solve it with better time complexity than the brute-force approach?
"""


def build_editorial_fallback(question):
    return f"""
### Intuition
The main idea is to recognize this as a **{question['topic']}** problem. Instead of only thinking about the sample input, identify the repeated pattern that works for all hidden test cases.

### Brute Force Approach
Try every possible candidate and check whether it satisfies the condition in the problem statement.

This is useful for understanding the problem, but it may be too slow when input size increases.

### Optimized Approach
{question['approach']}

### Step-by-Step Walkthrough
Use the sample input:

```text
{question['sample_input']}
```

Track your variables after every important operation. At the end, your program should produce:

```text
{question['sample_output']}
```

### Edge Cases
- Empty input
- One element input
- Duplicate values
- Already sorted or reverse sorted input
- No valid answer
- Very large input

### Complexity
- Time complexity: explain based on loops, recursion, or traversal count.
- Space complexity: explain based on extra arrays, maps, stacks, queues, or recursion depth.
"""


def explain_question_like_leetcode(question):
    fallback = build_editorial_fallback(question)
    prompt = f"""
Create a LeetCode-style full explanation/editorial for this coding problem.
Use this exact structure:
- Intuition
- Approach
- Algorithm
- Dry Run
- Correctness
- Complexity Analysis
- Edge Cases
- Interview Explanation

Make it detailed and student friendly. Do not give only a short summary.

Question:
{question}
"""
    return ai.generate(prompt, fallback=fallback)


def heuristic_code_score(question, code):
    code_lower = code.lower()
    score = 35
    if len(code.strip()) > 60:
        score += 15
    if any(token in code_lower for token in ["def ", "class ", "public", "function", "int main"]):
        score += 10
    if any(token in code_lower for token in ["return", "print", "cout", "system.out"]):
        score += 10
    if question["topic"].lower() in ["array", "string"] and any(token in code_lower for token in ["for", "while", "map", "dict", "set"]):
        score += 15
    if question["topic"].lower() in ["stack", "queue"] and any(token in code_lower for token in ["stack", "queue", "append", "pop", "deque"]):
        score += 15
    if question["topic"].lower() in ["dp", "tree", "graph", "backtracking"] and any(token in code_lower for token in ["dp", "dfs", "bfs", "rec", "memo", "queue"]):
        score += 15
    if any(token in code_lower for token in ["todo", "pass", "not sure"]):
        score -= 20
    return max(10, min(95, score))


def run_python_code(code, test_input, expected_output):
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "solution.py"
        file_path.write_text(code, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(file_path)],
                input=test_input,
                text=True,
                capture_output=True,
                timeout=3,
            )
            elapsed = int((time.perf_counter() - start) * 1000)
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            expected = expected_output.strip()
            passed = None
            if expected:
                passed = completed.returncode == 0 and normalize_output(stdout) == normalize_output(expected)
            return {"stdout": stdout, "stderr": stderr, "passed": passed, "time_ms": elapsed}
        except subprocess.TimeoutExpired:
            elapsed = int((time.perf_counter() - start) * 1000)
            return {
                "stdout": "",
                "stderr": "Execution timed out after 3 seconds. Check for infinite loops or very slow logic.",
                "passed": False,
                "time_ms": elapsed,
            }


def normalize_output(value):
    return "\n".join(line.rstrip() for line in value.strip().splitlines()).strip()
