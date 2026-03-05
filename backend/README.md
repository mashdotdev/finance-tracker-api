# Smart Finance Tracker API

A RESTful API for personal finance management, featuring JWT authentication, role-based access control, and an AI-powered finance assistant built with FastAPI and PostgreSQL.

## Features

- **Expense tracking** — Create, read, update, and delete expenses with category filtering
- **Budget management** — Set monthly budget limits per category with real-time spending summaries
- **Category organisation** — User-owned categories with cascade deletes
- **JWT authentication** — Access tokens + refresh tokens, signed with separate secrets
- **Argon2 password hashing** — Industry-standard, memory-hard hashing via `pwdlib`
- **Role-based access control** — `user` and `admin` roles with protected admin endpoints
- **AI finance assistant** — Conversational agent powered by Gemini 2.5 Flash with 4 function tools:
  - `get_spending_summary` — Total spending by category
  - `get_budget_status` — Budget health across all categories (over / approaching / within)
  - `get_top_expenses` — Biggest purchases this month
  - `can_afford_suggestion` — Affordability analysis based on live budget data

## Tech Stack

| Layer       | Technology                              |
| ----------- | --------------------------------------- |
| Framework   | FastAPI (async)                         |
| ORM         | SQLModel + SQLAlchemy async             |
| Database    | PostgreSQL (via asyncpg)                |
| Auth        | JWT (python-jose) + Argon2 (pwdlib)     |
| AI Agent    | OpenAI Agents SDK + Gemini 2.5 Flash    |
| Config      | pydantic-settings                       |
| Runtime     | Python 3.13+ / uv                       |

## Project Structure

```text
backend/
├── app/
│   ├── config.py        # Settings via pydantic-settings
│   ├── database.py      # Async engine, session factory, lifespan
│   └── exceptions.py    # Shared HTTP exception helpers
├── auth/
│   ├── security.py      # Password hashing, JWT create/decode
│   └── dependency.py    # get_current_user, require_admin
├── models/
│   ├── user_model.py
│   ├── expense_model.py
│   ├── category_model.py
│   └── budget_model.py
├── routes/
│   ├── user.py          # Register, login, refresh token, /me
│   ├── expense.py       # CRUD expenses
│   ├── category.py      # CRUD categories
│   ├── budget.py        # Budget CRUD + monthly summary
│   └── admin.py         # Admin-only user management
├── ai_agent/
│   ├── route.py         # POST /agent/chat
│   └── tools.py         # Function tools for the AI agent
└── app/main.py          # FastAPI app entry point
```

## Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL database
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A [Google AI Studio](https://aistudio.google.com/) API key for the AI agent

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd finance-tracker-api/backend

# Install dependencies
uv sync
# or: pip install -e .
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/finance_tracker

SECRET_KEY=your-secret-key
ALGORITHM=HS256
TOKEN_EXPIRE_TIME=30
REFRESH_TOKEN_SECRET_KEY=your-refresh-secret-key
REFRESH_ACCESS_TOKEN_EXPIRE_LIMIT=7

GEMINI_API_KEY=your-gemini-api-key
```

### Running

```bash
cd backend
uv run fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

## API Overview

### Authentication

| Method | Endpoint         | Description                                    |
| ------ | ---------------- | ---------------------------------------------- |
| POST   | `/users/create`  | Register a new user                            |
| POST   | `/users/token`   | Login — returns access + refresh tokens        |
| POST   | `/users/refresh` | Exchange refresh token for a new access token  |
| GET    | `/users/me`      | Get current user info                          |

### Categories

| Method | Endpoint             | Description                          |
| ------ | -------------------- | ------------------------------------ |
| GET    | `/categories`        | List all categories for current user |
| POST   | `/categories/create` | Create a category                    |
| DELETE | `/categories/{id}`   | Delete a category                    |

### Expenses

| Method | Endpoint            | Description                              |
| ------ | ------------------- | ---------------------------------------- |
| GET    | `/expenses`         | List expenses (optional `?category=`)    |
| POST   | `/expenses/create`  | Log a new expense                        |
| GET    | `/expenses/{id}`    | Get a specific expense                   |
| PUT    | `/expenses/{id}`    | Update an expense                        |
| DELETE | `/expenses/{id}`    | Delete an expense                        |

### Budgets

| Method | Endpoint                  | Description                              |
| ------ | ------------------------- | ---------------------------------------- |
| GET    | `/budget`                 | List all budgets                         |
| POST   | `/budget/create`          | Set a monthly budget for a category      |
| PUT    | `/budget/update/{id}`     | Update a budget limit                    |
| GET    | `/budget/summary`         | Monthly spending vs budget per category  |

### AI Agent

| Method | Endpoint       | Description                          |
| ------ | -------------- | ------------------------------------ |
| POST   | `/agent/chat`  | Chat with the finance AI assistant   |

**Example request:**

```json
POST /agent/chat
Authorization: Bearer <token>

{ "message": "Am I over budget this month?" }
```

### Admin

| Method | Endpoint                  | Description                          |
| ------ | ------------------------- | ------------------------------------ |
| DELETE | `/admin/users/{user_id}`  | Delete a user (admin role required)  |
