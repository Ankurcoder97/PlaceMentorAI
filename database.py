import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

import bcrypt

DB_PATH = Path("placementor.db")


COMPANIES = [
    "TCS", "Infosys", "Wipro", "Accenture", "Capgemini", "Cognizant",
    "Deloitte", "Amazon", "Microsoft", "Google", "Salesforce",
]

SUBJECTS = ["DBMS", "Operating System", "Computer Networks", "OOPs", "SQL", "DSA", "Software Engineering"]

APTITUDE_TOPICS = [
    "Number system", "Percentage", "Profit and loss", "Time and work",
    "Time, speed, distance", "Ratio and proportion", "Probability",
    "Permutation and combination", "Logical reasoning", "Verbal ability",
]


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def execute(query, params=(), fetchone=False, fetchall=False):
    with get_connection() as conn:
        cur = conn.execute(query, params)
        if fetchone:
            row = cur.fetchone()
            return dict(row) if row else None
        if fetchall:
            return [dict(row) for row in cur.fetchall()]
        return cur.lastrowid


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                branch TEXT DEFAULT '',
                year TEXT DEFAULT '',
                target_companies TEXT DEFAULT '[]',
                skills TEXT DEFAULT '',
                resume_text TEXT DEFAULT '',
                role TEXT DEFAULT 'student',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ats_score INTEGER,
                skills_match INTEGER,
                missing_keywords TEXT,
                feedback TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS company_preparation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company TEXT NOT NULL,
                status TEXT DEFAULT 'Not Started',
                content TEXT,
                completed INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS coding_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                statement TEXT NOT NULL,
                sample_input TEXT,
                sample_output TEXT,
                approach TEXT
            );
            CREATE TABLE IF NOT EXISTS solved_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                solution TEXT,
                status TEXT DEFAULT 'Solved',
                solved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, question_id)
            );
            CREATE TABLE IF NOT EXISTS coding_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                language TEXT DEFAULT 'Python',
                code TEXT NOT NULL,
                ai_score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Reviewed',
                feedback TEXT,
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS mock_interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                interview_type TEXT,
                company TEXT,
                transcript TEXT,
                communication_score INTEGER,
                technical_score INTEGER,
                confidence_score INTEGER,
                overall_score INTEGER,
                report TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS subject_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT DEFAULT '',
                score INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, subject, topic)
            );
            CREATE TABLE IF NOT EXISTS aptitude_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT,
                score INTEGER,
                total INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS roadmap_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_date TEXT,
                category TEXT,
                task TEXT,
                completed INTEGER DEFAULT 0
            );
            """
        )
    seed_database()


def seed_database():
    admin = get_user_by_email("admin@placementor.ai")
    if not admin:
        create_user(
            "Admin Mentor",
            "admin@placementor.ai",
            "admin123",
            branch="CSE",
            year="Final Year",
            target_companies=["TCS", "Amazon", "Microsoft"],
            skills="Python, SQL, DSA, DBMS, Communication",
            role="admin",
        )

    student = get_user_by_email("student@placementor.ai")
    if not student:
        create_user(
            "Demo Student",
            "student@placementor.ai",
            "student123",
            branch="Computer Science",
            year="Final Year",
            target_companies=["TCS", "Accenture", "Amazon"],
            skills="Python, Java, SQL, HTML, CSS, DSA",
            role="student",
        )

    if not execute("SELECT id FROM coding_questions LIMIT 1", fetchone=True):
        questions = [
            ("Two Sum", "Array", "Easy", "Find two indices whose values add to a target.", "nums=[2,7,11], target=9", "[0,1]", "Use a hash map to store complements."),
            ("Valid Parentheses", "Stack", "Easy", "Check if brackets are balanced.", "()[]{}", "true", "Push opening brackets, match on closing."),
            ("Reverse Linked List", "Linked List", "Easy", "Reverse a singly linked list iteratively.", "1->2->3", "3->2->1", "Track prev, current, and next pointers."),
            ("Longest Substring Without Repeat", "String", "Medium", "Find the longest substring with unique characters.", "abcabcbb", "3", "Use sliding window and last seen indexes."),
            ("Binary Search", "Binary Search", "Easy", "Search a sorted array in O(log n).", "[-1,0,3,5], target=3", "2", "Move low/high around mid."),
            ("Level Order Traversal", "Tree", "Medium", "Return binary tree nodes level by level.", "root=[3,9,20,null,null,15,7]", "[[3],[9,20],[15,7]]", "Use queue BFS."),
            ("Number of Islands", "Graph", "Medium", "Count connected groups of 1s in a grid.", "grid", "3", "DFS/BFS from unvisited land."),
            ("Climbing Stairs", "DP", "Easy", "Count ways to climb n stairs taking 1 or 2 steps.", "n=5", "8", "Fibonacci DP."),
            ("Activity Selection", "Greedy", "Medium", "Select max non-overlapping activities.", "start/end arrays", "max count", "Sort by finish time."),
            ("N Queens", "Backtracking", "Hard", "Place N queens so none attack each other.", "n=4", "2 solutions", "Backtrack row by row with safe columns/diagonals."),
        ]
        for q in questions:
            execute(
                """
                INSERT INTO coding_questions
                (title, topic, difficulty, statement, sample_input, sample_output, approach)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                q,
            )


def create_user(name, email, password, branch="", year="", target_companies=None, skills="", role="student"):
    target_companies = target_companies or []
    return execute(
        """
        INSERT INTO users (name, email, password_hash, branch, year, target_companies, skills, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, email.lower().strip(), hash_password(password), branch, year, json.dumps(target_companies), skills, role),
    )


def get_user_by_email(email):
    return execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),), fetchone=True)


def get_user(user_id):
    return execute("SELECT * FROM users WHERE id = ?", (user_id,), fetchone=True)


def update_user_profile(user_id, name, branch, year, target_companies, skills, resume_text=""):
    execute(
        """
        UPDATE users
        SET name=?, branch=?, year=?, target_companies=?, skills=?, resume_text=?
        WHERE id=?
        """,
        (name, branch, year, json.dumps(target_companies), skills, resume_text, user_id),
    )


def list_users():
    return execute("SELECT id, name, email, branch, year, role, created_at FROM users ORDER BY created_at DESC", fetchall=True)


def save_resume_result(user_id, result):
    execute(
        """
        INSERT INTO resumes (user_id, ats_score, skills_match, missing_keywords, feedback)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            result.get("ats_score", 0),
            result.get("skills_match", 0),
            ", ".join(result.get("missing_keywords", [])),
            json.dumps(result),
        ),
    )


def get_resume_history(user_id):
    return execute("SELECT * FROM resumes WHERE user_id=? ORDER BY created_at", (user_id,), fetchall=True)


def get_coding_questions(topic=None, difficulty=None):
    query = "SELECT * FROM coding_questions WHERE 1=1"
    params = []
    if topic and topic != "All":
        query += " AND topic=?"
        params.append(topic)
    if difficulty and difficulty != "All":
        query += " AND difficulty=?"
        params.append(difficulty)
    return execute(query + " ORDER BY topic, difficulty", tuple(params), fetchall=True)


def add_coding_question(title, topic, difficulty, statement, sample_input="", sample_output="", approach=""):
    return execute(
        """
        INSERT INTO coding_questions (title, topic, difficulty, statement, sample_input, sample_output, approach)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (title, topic, difficulty, statement, sample_input, sample_output, approach),
    )


def mark_question_solved(user_id, question_id, solution):
    execute(
        """
        INSERT INTO solved_questions (user_id, question_id, solution)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, question_id) DO UPDATE SET solution=excluded.solution, solved_at=CURRENT_TIMESTAMP
        """,
        (user_id, question_id, solution),
    )


def save_code_submission(user_id, question_id, language, code, ai_score, status, feedback):
    submission_id = execute(
        """
        INSERT INTO coding_submissions
        (user_id, question_id, language, code, ai_score, status, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, question_id, language, code, ai_score, status, feedback),
    )
    if ai_score >= 70:
        mark_question_solved(user_id, question_id, code)
    return submission_id


def get_code_submissions(user_id, question_id=None):
    query = """
        SELECT cs.*, cq.title, cq.topic, cq.difficulty
        FROM coding_submissions cs
        JOIN coding_questions cq ON cq.id = cs.question_id
        WHERE cs.user_id=?
    """
    params = [user_id]
    if question_id:
        query += " AND cs.question_id=?"
        params.append(question_id)
    query += " ORDER BY cs.submitted_at DESC"
    return execute(query, tuple(params), fetchall=True)


def get_solved_questions(user_id):
    return execute(
        """
        SELECT sq.*, cq.title, cq.topic, cq.difficulty
        FROM solved_questions sq
        JOIN coding_questions cq ON cq.id = sq.question_id
        WHERE sq.user_id=?
        ORDER BY sq.solved_at DESC
        """,
        (user_id,),
        fetchall=True,
    )


def save_subject_progress(user_id, subject, topic, score, completed):
    execute(
        """
        INSERT INTO subject_progress (user_id, subject, topic, score, completed)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, subject, topic)
        DO UPDATE SET score=excluded.score, completed=excluded.completed, updated_at=CURRENT_TIMESTAMP
        """,
        (user_id, subject, topic, score, int(completed)),
    )


def get_subject_progress(user_id):
    return execute("SELECT * FROM subject_progress WHERE user_id=?", (user_id,), fetchall=True)


def save_aptitude_score(user_id, topic, score, total):
    execute("INSERT INTO aptitude_scores (user_id, topic, score, total) VALUES (?, ?, ?, ?)", (user_id, topic, score, total))


def get_aptitude_scores(user_id):
    return execute("SELECT * FROM aptitude_scores WHERE user_id=? ORDER BY created_at", (user_id,), fetchall=True)


def save_mock_interview(user_id, interview_type, company, transcript, scores, report):
    execute(
        """
        INSERT INTO mock_interviews
        (user_id, interview_type, company, transcript, communication_score, technical_score, confidence_score, overall_score, report)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            interview_type,
            company,
            json.dumps(transcript),
            scores.get("communication", 0),
            scores.get("technical", 0),
            scores.get("confidence", 0),
            scores.get("overall", 0),
            report,
        ),
    )


def get_mock_interviews(user_id):
    return execute("SELECT * FROM mock_interviews WHERE user_id=? ORDER BY created_at", (user_id,), fetchall=True)


def save_company_prep(user_id, company, content, completed=False):
    execute(
        """
        INSERT INTO company_preparation (user_id, company, content, status, completed, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (user_id, company, content, "Completed" if completed else "In Progress", int(completed)),
    )


def get_company_prep(user_id):
    return execute("SELECT * FROM company_preparation WHERE user_id=? ORDER BY updated_at DESC", (user_id,), fetchall=True)


def add_roadmap_tasks(user_id, tasks):
    for task in tasks:
        execute(
            "INSERT INTO roadmap_tasks (user_id, task_date, category, task, completed) VALUES (?, ?, ?, ?, ?)",
            (user_id, task.get("date", str(date.today())), task.get("category", "General"), task.get("task", ""), int(task.get("completed", False))),
        )


def get_roadmap_tasks(user_id):
    return execute("SELECT * FROM roadmap_tasks WHERE user_id=? ORDER BY task_date, id", (user_id,), fetchall=True)


def toggle_task(task_id, completed):
    execute("UPDATE roadmap_tasks SET completed=? WHERE id=?", (int(completed), task_id))


def metrics_for_user(user_id):
    total_questions = execute("SELECT COUNT(*) AS c FROM coding_questions", fetchone=True)["c"]
    solved = len(get_solved_questions(user_id))
    resumes = get_resume_history(user_id)
    subjects = get_subject_progress(user_id)
    interviews = get_mock_interviews(user_id)
    aptitude = get_aptitude_scores(user_id)
    company = get_company_prep(user_id)
    resume_score = resumes[-1]["ats_score"] if resumes else 62
    coding_score = int((solved / max(total_questions, 1)) * 100)
    core_score = int(sum(s["score"] for s in subjects) / max(len(subjects), 1)) if subjects else 45
    interview_score = int(sum(i["overall_score"] for i in interviews) / max(len(interviews), 1)) if interviews else 50
    aptitude_score = int(sum((a["score"] / max(a["total"], 1)) * 100 for a in aptitude) / max(len(aptitude), 1)) if aptitude else 55
    readiness = int((resume_score + coding_score + core_score + interview_score + aptitude_score) / 5)
    weak = []
    for label, score in [
        ("Resume", resume_score),
        ("Coding", coding_score),
        ("Core CS", core_score),
        ("Interview", interview_score),
        ("Aptitude", aptitude_score),
    ]:
        if score < 70:
            weak.append(label)
    return {
        "readiness": readiness,
        "resume": resume_score,
        "coding": coding_score,
        "core": core_score,
        "interview": interview_score,
        "aptitude": aptitude_score,
        "weak_areas": weak or ["Keep revising and attempt company mocks"],
        "solved": solved,
        "total_questions": total_questions,
        "company_completed": sum(1 for c in company if c["completed"]),
    }


def today_tasks(user):
    targets = json.loads(user.get("target_companies") or "[]")
    company = targets[0] if targets else "your top company"
    return [
        f"Solve 2 DSA problems focused on arrays or strings for {company}.",
        "Revise one DBMS topic and attempt its quiz.",
        "Improve one resume bullet with impact metrics.",
        "Practice a 45-second self introduction aloud.",
    ]
