# prepNinja | PlaceMentor AI

prepNinja, also called PlaceMentor AI in the codebase, is an end-to-end placement preparation platform built for engineering students. It helps a student prepare for campus placements from one place: resume analysis, company-wise preparation, DSA practice, core CS revision, aptitude practice, AI mock interviews, HR answer improvement, project explanation training, roadmap generation, progress tracking, and admin monitoring.

The main idea of this project is to behave like a personal placement mentor. A student can log in, maintain a profile, choose target companies, upload or paste a resume, practice coding and aptitude, take mock interviews, and track readiness through a dashboard.

## Problem Statement

Engineering students usually prepare for placements using many disconnected resources: resume tools, DSA sheets, company PDFs, aptitude sites, YouTube videos, mock interviews, and handwritten progress trackers. Because everything is scattered, students often do not know their weak areas or what to prepare next.

This project solves that problem by creating a single AI-assisted platform where preparation is structured, measurable, and personalized.

## Objectives

- Provide one dashboard for complete placement preparation.
- Analyze resumes with ATS-style scoring and company-specific keyword feedback.
- Generate company-wise preparation plans for service-based and product-based companies.
- Offer coding practice with AI review, hints, debugging help, and solved tracking.
- Help students revise core CS subjects like DBMS, OS, CN, OOPs, SQL, DSA, and Software Engineering.
- Conduct AI-style mock interviews and save interview reports.
- Improve HR answers and project explanations for real interviews.
- Track readiness score, weak areas, roadmap tasks, and preparation history.
- Provide an admin panel for adding coding questions and checking student progress.

## Tech Stack

### Frontend

- Streamlit
- Custom HTML/CSS injected inside Streamlit for a polished dark UI
- Streamlit components such as forms, tabs, expanders, metrics, progress bars, charts, file uploader, radio buttons, and select boxes

### Backend

- Python
- Modular Python files for each feature area
- Session-based app flow using `st.session_state`

### Database

- SQLite
- `sqlite3` Python module
- Local database file: `placementor.db`

### Authentication

- Local signup and login
- Password hashing with `bcrypt`
- Student and admin roles

### AI Integration

- OpenAI Python SDK
- Environment-based API configuration using `.env`
- Local fallback responses when no API key is available or API call fails

### Data and Visualization

- pandas
- plotly
- Streamlit charts

### Resume Parsing

- pdfplumber
- PyPDF2 fallback parser
- Regex-based keyword and section analysis

## Main Features

## 1. Authentication and Profile

Students can sign up and log in using email and password. Passwords are not stored directly; they are hashed using bcrypt before saving in SQLite.

Each student profile stores:

- Name
- Email
- Branch
- Year
- Target companies
- Skills
- Resume text
- Role: student or admin

Demo accounts are seeded automatically:

- Student: `student@placementor.ai` / `student123`
- Admin: `admin@placementor.ai` / `admin123`

## 2. Dashboard

The dashboard gives a quick overview of placement preparation. It shows:

- Overall readiness score
- Resume score
- Coding progress
- Core CS progress
- Interview progress
- Aptitude progress
- Weak areas
- Daily preparation tasks
- Progress chart using Plotly

The readiness score is calculated from user activity stored in the database. This makes the dashboard dynamic instead of static.

## 3. Resume Analyzer

The resume analyzer accepts either:

- PDF upload
- Manually pasted resume text

It extracts text using `pdfplumber`, and if that fails, it tries `PyPDF2`.

The analyzer checks:

- Resume sections such as education, skills, projects, experience, and achievements
- Company-specific keywords
- Student profile skills
- Action verbs
- Quantified achievements
- Grammar-style spacing issues
- Project quality
- Experience quality
- Formatting quality

It then generates:

- ATS score
- Skills match percentage
- Missing keywords
- Improvement suggestions
- AI feedback

The result is saved in the `resumes` table so the student can track resume improvement over time.

## 4. Company-Wise Preparation Agent

This module helps students prepare for target companies such as:

- TCS
- Infosys
- Wipro
- Accenture
- Capgemini
- Cognizant
- Deloitte
- Amazon
- Microsoft
- Google
- Salesforce

For each company, the app can generate:

- Hiring process overview
- Expected rounds
- Aptitude topics
- Coding topics
- Core CS topics
- HR questions
- Technical questions
- 7-day, 15-day, or 30-day preparation plan
- Resume tips
- Company-specific practice questions

The app supports question generation by category:

- Mixed
- Coding
- Technical
- HR
- Aptitude

Generated plans are saved in the database.

## 5. Coding Platform

The coding platform contains seeded DSA problems and allows the student to practice by topic and difficulty.

It includes:

- Problem selection
- Topic filter
- Difficulty filter
- Code editor
- Language selection: Python, Java, C++, JavaScript
- Problem statement
- Sample input and output
- Approach explanation
- AI explain button
- Hint button
- Logic checking
- Bug finding
- Optimization suggestions
- AI code review score
- Submission history
- Manual solved tracking

Seeded topics include:

- Array
- String
- Linked List
- Stack
- Tree
- Graph
- DP
- Greedy
- Backtracking
- Binary Search

Submissions are stored in `coding_submissions`, and solved questions are stored in `solved_questions`.

## 6. Core Subjects

This module helps students revise important CS fundamentals for interviews.

Subjects include:

- DBMS
- Operating System
- Computer Networks
- OOPs
- SQL
- DSA
- Software Engineering

Students can:

- Select a subject
- Select a topic
- Read notes
- Generate interview questions
- Practice short answers
- Check answers using AI feedback
- Mark topics as completed

Progress is stored in the `subject_progress` table.

## 7. AI Mock Interview

The mock interview module conducts one-question-at-a-time interviews.

Interview types include:

- HR interview
- Technical interview
- DSA interview
- Project-based interview
- Company-specific interview

Flow:

1. Student chooses interview type and company.
2. App asks one question.
3. Student writes an answer.
4. AI gives feedback and an improved answer.
5. App moves to the next question.
6. At the end, the app generates a final report.

The final report includes:

- Communication score
- Technical score
- Confidence score
- Overall score
- Improvement areas
- Better answer pattern

Saved reports are stored in `mock_interviews`.

## 8. Aptitude Practice

The aptitude module helps students prepare for common placement aptitude rounds.

Topics include:

- Number system
- Percentage
- Profit and loss
- Time and work
- Time, speed, distance
- Ratio and proportion
- Probability
- Permutation and combination
- Logical reasoning
- Verbal ability

It supports:

- Formula revision
- Difficulty selection
- AI-generated questions
- MCQ quiz attempt
- Score calculation
- Explanation-based learning
- Attempt history

Scores are saved in `aptitude_scores`.

## 9. Project Trainer

The project trainer helps a student explain their project professionally in interviews.

It generates:

- Interview-level project explanation
- Tech stack explanation
- Challenges faced
- Why the project was useful
- Future scope
- Possible interviewer questions

This is useful because many students build projects but struggle to explain architecture, design choices, and impact clearly.

## 10. HR Trainer

The HR trainer improves answers for common interview prompts like:

- Tell me about yourself
- Why should we hire you?
- What are your strengths and weaknesses?
- Why this company?
- Explain your career goals

It generates:

- Improved answer
- 20-second version
- 45-second version
- 1-minute version

This helps students prepare answers based on different interview situations.

## 11. Roadmap Generator

The roadmap generator creates a 7-day placement preparation plan based on the student's profile and weak areas.

It creates tasks for:

- DSA
- Core CS
- Company preparation

Students can mark tasks as complete, and the status is saved in `roadmap_tasks`.

## 12. Progress Tracker

The progress tracker shows historical performance from different modules.

It displays:

- Resume score history
- Solved coding problems by topic
- Core subject scores
- Aptitude attempts
- Mock interview scores
- Company plan count

This gives a measurable view of preparation instead of only showing content.

## 13. Admin Panel

The admin panel is available only for admin users.

Admin can:

- Add new coding questions
- View registered users
- Check student progress by user ID

This makes the project useful not only for students but also for mentors or placement trainers.

## Project Structure

```text
Placement_prep/
├── app.py                 # Main Streamlit app, navigation, admin, HR trainer, project trainer
├── auth.py                # Login, signup, logout, profile management
├── database.py            # SQLite schema, seed data, CRUD helpers, metrics
├── ai_service.py          # OpenAI integration and local fallback AI responses
├── dashboard.py           # Dashboard, progress tracker, roadmap generator
├── resume_analyzer.py     # PDF extraction and ATS-style resume analysis
├── company_prep.py        # Company-wise plans and question generator
├── coding_platform.py     # Coding practice, AI review, solved tracking
├── core_subjects.py       # Core CS notes, MCQs, answer checking
├── aptitude.py            # Aptitude formulas, quizzes, scoring
├── interview_agent.py     # Mock interview flow and reports
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── placementor.db         # SQLite database, generated/seeded locally
└── logo.jpeg              # App logo
```

## Database Design

The app uses SQLite because it is simple, lightweight, and perfect for a local prototype or college project demo.

Main tables:

- `users`: stores student/admin profile and authentication data
- `resumes`: stores resume analysis history
- `company_preparation`: stores generated company plans and questions
- `coding_questions`: stores DSA practice questions
- `solved_questions`: stores solved problem records
- `coding_submissions`: stores submitted code and AI review feedback
- `mock_interviews`: stores mock interview transcripts and reports
- `subject_progress`: stores core CS progress
- `aptitude_scores`: stores aptitude quiz attempts
- `roadmap_tasks`: stores generated preparation tasks

## AI Design

The AI logic is centralized in `ai_service.py`.

The `AIService` class:

- Loads `OPENAI_API_KEY` and `OPENAI_MODEL` from environment variables.
- Calls the OpenAI API when a key is available.
- Returns fallback content when no API key is configured.
- Handles exceptions so the app does not crash during demos.

This is an important design decision. Even if the API key is missing, expired, or internet is unavailable, the app still works with structured fallback responses.

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env`.

On Windows:

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Then update:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

The app can run without an API key because fallback responses are available.

Important: Do not commit a real API key to GitHub. Keep real secrets only in `.env`.

### 5. Run the App

```bash
streamlit run app.py
```

The app will open in the browser, usually at:

```text
http://localhost:8501
```

## How to Use the App

1. Start the app using `streamlit run app.py`.
2. Log in using the demo student account or create a new account.
3. Complete the profile with branch, year, skills, and target companies.
4. Upload or paste a resume in Resume Analyzer.
5. Generate company preparation plans.
6. Practice coding questions and submit code for AI review.
7. Revise core subjects and mark topics completed.
8. Attempt aptitude quizzes.
9. Take AI mock interviews and save reports.
10. Use HR Trainer and Project Trainer before real interviews.
11. Track progress from Dashboard and Progress pages.

## How to Explain This Project in an Interview

Below is a 20-minute teacher-style explanation you can use in an interview. Speak slowly and explain the project like you are teaching the interviewer how the system works.

### Minute 0-2: Introduction

"My project is called prepNinja, also known as PlaceMentor AI. It is an AI-assisted placement preparation platform for engineering students. The goal is to bring all important placement preparation activities into one platform: resume analysis, company preparation, coding practice, aptitude, core CS revision, mock interviews, HR practice, project explanation, roadmap generation, and progress tracking.

The problem I observed is that students usually prepare from many different resources. Resume tools are separate, DSA sheets are separate, aptitude practice is separate, and mock interviews are separate. Because of that, students do not get a clear picture of their readiness. So I built a system where a student can prepare, get feedback, and track progress from one dashboard."

### Minute 2-4: User Roles and Authentication

"The application has two roles: student and admin. A student can sign up, log in, update profile, practice modules, and track progress. An admin can add coding questions and view student progress.

For authentication, I used local email-password login. I do not store plain passwords. I hash passwords using bcrypt and store only the hashed password in SQLite. During login, the entered password is checked against the saved hash. This is a basic but important security practice."

### Minute 4-6: Tech Stack

"The frontend is built with Streamlit because it allows fast development of Python-based dashboards and interactive tools. I also used custom CSS to improve the visual design and make the app look more polished.

The backend is Python. Each major feature is separated into its own module, for example resume analyzer, coding platform, mock interview, aptitude, dashboard, and database.

For the database, I used SQLite. It is lightweight and does not require a separate server, which makes it suitable for local demos and student projects. The database stores users, resumes, coding submissions, solved questions, interview reports, aptitude scores, subject progress, company plans, and roadmap tasks.

For AI, I integrated the OpenAI SDK. The API key and model are loaded from the `.env` file. I also added fallback responses, so even if the API is unavailable, the app continues working.


### Minute 6-8: Architecture

"The architecture is modular. `app.py` is the main entry point. It sets the Streamlit page configuration, applies CSS, initializes the database, handles navigation, and calls the correct render function based on the selected page.

`database.py` handles all database operations. It creates tables, seeds demo users and sample coding questions, and provides helper functions to save and fetch data.

`ai_service.py` handles all AI calls in one place. This avoids repeating API code in every module. Other modules call this service whenever they need AI feedback.

Feature modules are separated. For example, resume logic is in `resume_analyzer.py`, company preparation is in `company_prep.py`, mock interview logic is in `interview_agent.py`, and so on. This makes the code easier to maintain and explain."

### Minute 8-10: Resume Analyzer

"The resume analyzer accepts a PDF file or pasted text. If the user uploads a PDF, I first try extracting text with pdfplumber. If that fails, I use PyPDF2 as a fallback.

After extracting text, the system checks important resume signals. It checks whether sections like education, skills, projects, experience, and achievements are present. It also checks company-specific keywords. For example, Amazon focuses more on DSA, system design, leadership, and scalability, while TCS may focus on Java, SQL, OOP, aptitude, communication, and SDLC.

The analyzer calculates ATS score, skills match percentage, missing keywords, grammar-style issues, project quality, experience quality, and formatting feedback. Then AI feedback is generated and the result is saved to the database so the student can track improvement over time."

### Minute 10-12: Company Prep and Coding Platform

"The company preparation module allows students to select a company and generate a 7-day, 15-day, or 30-day preparation plan. It includes hiring process, expected rounds, coding topics, aptitude topics, core subjects, HR questions, technical questions, and resume tips.

The coding platform is like a mini DSA practice system. It has seeded questions such as Two Sum, Valid Parentheses, Binary Search, Number of Islands, N Queens, and more. A student can filter by topic and difficulty, write code, get hints, get explanation, check logic, find bugs, optimize the solution, submit for AI review, and mark a question as solved.

The app stores solved questions and code submissions. This data contributes to the student's progress and readiness score."

### Minute 12-14: Core Subjects and Aptitude

"For core subjects, I included important interview subjects such as DBMS, Operating System, Computer Networks, OOPs, SQL, DSA, and Software Engineering. Students can revise notes, generate interview questions, practice answers, and mark topics as complete.

For aptitude, I added common placement topics such as percentage, profit and loss, time and work, probability, permutation and combination, logical reasoning, and verbal ability. The student can generate questions, attempt quizzes, submit answers, view scores, and learn from explanations.

Both core subject progress and aptitude scores are stored in the database, so the platform can show preparation history."

### Minute 14-16: Mock Interview, HR Trainer, and Project Trainer

"The mock interview module simulates an interview by asking one question at a time. The student chooses an interview type such as HR, technical, DSA, project-based, or company-specific. After every answer, the AI gives feedback and a better answer. At the end, the system generates a report with communication score, technical score, confidence score, overall score, and improvement areas.

The HR trainer helps students improve answers for questions like 'Tell me about yourself' and 'Why should we hire you?' It gives multiple versions such as 20-second, 45-second, and 1-minute answers.

The project trainer helps students explain their own project clearly. It covers project objective, tech stack, architecture, challenges, future scope, and possible interviewer questions. This is very useful because interviewers often ask students to explain their project in detail."

### Minute 16-18: Dashboard, Readiness Score, and Progress Tracking

"The dashboard is the central view of the application. It shows the student's overall readiness, resume score, coding score, core CS score, interview score, aptitude score, weak areas, and daily tasks.

The progress tracker shows historical performance using charts. For example, resume score history, solved coding problems by topic, core subject scores, aptitude attempts, and mock interview scores.

The readiness score is calculated from multiple activities, not from only one input. This is important because placement readiness is not just about DSA or resume. It includes resume quality, coding practice, aptitude, CS fundamentals, interview performance, and consistency."

### Minute 18-20: Challenges, Learning, and Future Scope

"One challenge was designing the app in a modular way so that each feature remained understandable and maintainable. I solved this by separating every major feature into a different Python file.

Another challenge was making the AI integration reliable. If the API fails during a demo, the app should not break. So I added fallback responses in `ai_service.py`.

I also learned how to design a database schema for a real application. The project has multiple connected entities such as users, resumes, coding submissions, interviews, and progress records.

In future, I can improve this project by adding cloud deployment, real test-case execution for code submissions, better role-based access control, analytics for mentors, email reminders, leaderboard, resume version comparison, and integration with job portals or college placement cells."

## Short Interview Summary

If the interviewer asks for a short explanation, say this:

"prepNinja is an AI-assisted placement preparation platform built with Python, Streamlit, SQLite, and OpenAI. It helps engineering students prepare for placements through resume analysis, company-wise plans, DSA practice, aptitude quizzes, core CS revision, mock interviews, HR answer improvement, project explanation, roadmap generation, and progress tracking. I used bcrypt for password hashing, SQLite for persistence, modular Python files for maintainability, Plotly for analytics, and an AI service layer with fallback responses so the app remains reliable during demos."

## Important Code Files to Mention

- `app.py`: Main entry point, navigation, styling, admin panel, HR trainer, project trainer
- `database.py`: Table creation, seed data, CRUD operations, progress metrics
- `auth.py`: Login, signup, profile update, bcrypt password verification
- `ai_service.py`: OpenAI API wrapper and fallback responses
- `resume_analyzer.py`: PDF text extraction and ATS-style scoring
- `company_prep.py`: Company plans and question generation
- `coding_platform.py`: DSA practice, AI review, solved tracking
- `core_subjects.py`: CS revision and progress
- `aptitude.py`: Aptitude quiz and score saving
- `interview_agent.py`: Mock interview and final report
- `dashboard.py`: Readiness dashboard, roadmap, and progress charts

## Possible Interview Questions and Answers

### Why did you choose Streamlit?

I chose Streamlit because this project is data-driven and interactive. Streamlit lets me build dashboards, forms, file upload, charts, and multipage workflows quickly using Python. It is suitable for rapid prototyping and college project demos.

### Why SQLite?

SQLite is lightweight, serverless, and easy to set up. Since this is a local prototype, SQLite is enough. If I scale the project, I can migrate to PostgreSQL or MySQL.

### How is password security handled?

Passwords are hashed using bcrypt. The plain password is never stored in the database. During login, bcrypt compares the entered password with the stored hash.

### What happens if OpenAI API is not available?

The app still works because `ai_service.py` provides fallback responses. This makes the demo reliable even without internet or API key.

### How is resume score calculated?

The resume score is calculated using resume sections, company keywords, student skills, action verbs, measurable numbers, and formatting signals. AI feedback is then added for better suggestions.

### How do you calculate readiness?

Readiness is calculated from multiple preparation areas such as resume score, coding solved count, core subject progress, mock interview score, and aptitude performance.

### How would you scale this project?

I would deploy the app on the cloud, replace SQLite with PostgreSQL, add secure authentication with JWT or OAuth, add real code execution using sandboxing, store files in cloud storage, and add mentor dashboards for institutions.

## Future Enhancements

- Cloud deployment
- PostgreSQL or MySQL database
- Real coding test-case execution
- Resume version comparison
- More detailed AI interview reports
- Mentor dashboard for colleges
- Leaderboard and streak tracking
- Email reminders for roadmap tasks
- Company-wise previous year question bank
- Role-based access control with stronger authorization
- Exportable PDF reports

## Conclusion

prepNinja is a complete placement preparation assistant that combines AI, structured practice, database persistence, analytics, and interview training. It is useful as a student project because it demonstrates frontend development, backend logic, database design, authentication, AI integration, file handling, analytics, and practical problem solving in one application.
