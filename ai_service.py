import os
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, system: str = "You are PlaceMentor AI, a practical placement preparation mentor.", fallback: str = "") -> str:
        if not self.available():
            return fallback or self.local_fallback(prompt)
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return fallback or self.local_fallback(prompt)

    def local_fallback(self, prompt: str) -> str:
        return dedent(
            """
            ### AI Mentor Suggestions
            - Focus on clarity, measurable impact, and fundamentals.
            - Use the STAR format for behavioral answers: Situation, Task, Action, Result.
            - For coding, explain brute force first, then optimize using data structures.
            - For resumes, add numbers, technologies, and outcomes in each project bullet.
            - For company prep, revise aptitude, DSA basics, DBMS, OOPs, OS, and communication.

            Set `OPENAI_API_KEY` in `.env` to enable live personalized AI responses.
            """
        ).strip()


ai = AIService()


def improve_answer(question, answer, context=""):
    fallback = f"""
### Feedback
Score: 7/10

Your answer is relevant. Improve it by adding structure, one concrete example, and a measurable result.

### Better Answer
For "{question}", I would answer with a short context, the action I took, the result, and what I learned. {context}
"""
    return ai.generate(f"Question: {question}\nAnswer: {answer}\nContext: {context}\nGive feedback, score, and a better answer.", fallback=fallback)


def generate_project_explanation(details):
    fallback = f"""
### Interview-Level Explanation
My project solves a real user problem by combining a clean frontend, reliable backend logic, and data-driven decisions. The main workflow is: user input, validation, processing, storage, and result visualization.

### Tech Stack Explanation
I selected the stack because it is simple to deploy, easy to iterate, and suitable for building a functional prototype quickly.

### Challenges Faced
- Designing a clean data flow
- Handling edge cases and user errors
- Making the UI simple for non-technical users

### Why This Project?
It shows practical engineering skills: problem solving, database design, APIs, UI thinking, and testing.

### Future Scope
- Authentication and roles
- Analytics dashboard
- Cloud deployment
- Better AI recommendations

### Possible Interviewer Questions
- What problem does this project solve?
- Why did you choose this tech stack?
- What was the hardest bug?
- How would you scale it?

Project details used: {details[:500]}
"""
    return ai.generate(f"Generate a polished project explanation trainer response for:\n{details}", fallback=fallback)


def generate_hr_answer(prompt_name, user_answer, profile):
    fallback = f"""
### Improved Answer
I am a {profile.get('branch', 'engineering')} student with skills in {profile.get('skills', 'programming and problem solving')}. I enjoy building practical projects, learning quickly, and working with teams. {user_answer}

### 20-Second Version
I am an engineering student focused on software development, DSA, and practical projects. I learn quickly and enjoy solving real problems.

### 45-Second Version
I am an engineering student with hands-on experience in projects and core CS fundamentals. I have worked with technologies like {profile.get('skills', 'Python and SQL')} and I am preparing for roles where I can contribute, learn, and grow.

### 1-Minute Version
I am a motivated engineering student with a strong interest in software development and placement preparation. My strengths are consistency, problem solving, and learning new tools quickly. I have practiced DSA, core subjects, and project building, and I want to join a company where I can apply these skills to real business problems.
"""
    return ai.generate(f"Prompt: {prompt_name}\nUser answer: {user_answer}\nProfile: {profile}\nImprove and produce 20s, 45s, 1min versions.", fallback=fallback)
