# PlaceMentor AI

PlaceMentor AI is a Streamlit-based placement preparation platform for engineering students. It includes resume analysis, company-wise preparation, coding practice, core CS revision, aptitude quizzes, AI mock interviews, project explanation training, HR communication practice, roadmap generation, progress tracking, and an admin panel.

## Features

- Local signup/login with bcrypt password hashing
- Student profile with branch, year, skills, resume text, and target companies
- Dashboard with readiness score, weak areas, daily tasks, and charts
- PDF resume analyzer with ATS scoring, keyword gaps, formatting feedback, and AI suggestions
- Company preparation plans for TCS, Infosys, Wipro, Accenture, Capgemini, Cognizant, Deloitte, Amazon, Microsoft, Google, and Salesforce
- GPT-style company question generator for coding, technical, HR, aptitude, and mixed practice questions
- Coding practice platform with seeded DSA questions, code editor, in-app code submission, AI review score, feedback, debugging, optimization, and solved tracking
- Core CS notes, MCQs, short-answer practice, and weak topic tracking
- AI mock interviews with one-question-at-a-time flow, feedback, ratings, and reports
- Aptitude formulas, quiz attempts, scoring, and explanations
- Project and HR trainers with interview-ready answer generation
- Roadmap generator and progress analytics
- Admin panel for adding coding questions and viewing student progress

## Tech Stack

- Frontend: Streamlit
- Backend: Python
- Database: SQLite
- AI: OpenAI API with local fallback responses
- Libraries: pandas, plotly, pdfplumber, PyPDF2, bcrypt, python-dotenv

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Demo Accounts

- Student: `student@placementor.ai` / `student123`
- Admin: `admin@placementor.ai` / `admin123`

The SQLite database `placementor.db` is created automatically on first run with sample users and coding questions.

## AI Configuration

The app works without an API key using structured fallback content. To enable live AI responses:

1. Copy `.env.example` to `.env`.
2. Set `OPENAI_API_KEY`.
3. Optionally change `OPENAI_MODEL`.
4. Restart Streamlit.

## Project Structure

- `app.py`: Streamlit entrypoint, navigation, admin, project trainer, HR trainer
- `auth.py`: Signup, login, logout, profile management
- `database.py`: SQLite schema, seed data, persistence helpers, metrics
- `ai_service.py`: OpenAI integration and fallback AI responses
- `resume_analyzer.py`: PDF extraction and ATS-style resume scoring
- `company_prep.py`: Company-wise preparation generator
- `coding_platform.py`: Coding practice and solved tracking
- `coding_platform.py`: Coding practice, AI review, submission history, and solved tracking
- `core_subjects.py`: Notes, MCQs, short-answer practice
- `aptitude.py`: Aptitude formulas and quizzes
- `interview_agent.py`: Mock interview flow and report generation
- `dashboard.py`: Dashboard, roadmap, and progress views

## Portfolio Tips

- Add screenshots of the dashboard, resume analyzer, mock interview, and progress tracker.
- Record a short demo showing the app working without an API key, then with OpenAI enabled.
- Mention the fallback design because it makes the project reliable during demos.
- Explain the readiness score as a weighted combination of resume, coding, core CS, interview, and aptitude progress.
