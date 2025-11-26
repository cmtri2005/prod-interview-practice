# Interview Practice Platform

This platform combines FastAPI, LangGraph, and modern LLM providers (GROQ or Bedrock) to help engineers prepare for interviews. It automates three core workflows:
- Parse a Job Description (JD) and turn it into an actionable learning plan.
- Analyze every learning module with RAG-backed context so learners get the most relevant resources.
- Generate CLI-style quizzes for any topic/difficulty, store history in Postgres, and grade answers via LLM reasoning.

## Key Directories
| `main.py` | Boots FastAPI and mounts the API router. |
| `apps/api/router.py` | Lists every REST endpoint for learning progress and quizzes. |
| `apps/langgraph/core/agents` | LangGraph agents (JD extraction, learning plan, module analyzer, quiz, RAG). |
| `apps/langgraph/schema` | Pydantic schemas for JD, learning progress, and quiz payloads. |
| `apps/langgraph/data/quiz.py` | Data access helpers for Postgres. |
| `apps/db` | SQLAlchemy engine/session plus schema initialization scripts. |
| `apps/helper` | Logger + config/exception helpers. |
| `apps/chroma_db` | Dockerized Postgres + Chroma playground for vector experiments. |

## System Requirements

- Python 3.11+ (matches the `Dockerfile` base image).
- pip/virtualenv.
- Local Postgres 14+ (default host `127.0.0.1`, port `5432`).
- GROQ account (for `ChatGroq`) and/or Bedrock access (for quizzes).
- AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) when using Bedrock.
- Optional: Docker & Docker Compose for `apps/chroma_db`, plus a Hugging Face API key for embedding services.

## Environment Setup
```bash
git clone <repo>
cd prod-interview-practice
python -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -r requirements.txt

## Running the Services
### Local dev (hot reload)
```bash
uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```
Swagger docs live at `http://localhost:8008/docs`.

### Docker
```bash
docker build -t interview-api .
docker run -p 8008:8000 --env-file .env interview-api
```