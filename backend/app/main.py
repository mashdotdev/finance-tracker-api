from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import (
    category_router,
    authentication_router,
    expense_router,
    budget_router,
    admin_router,
)
from ai_agent import agent_router
from app import lifespan

app = FastAPI(
    title="Smart Finance Tracker API",
    description="AI powered finance tracker api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category_router)
app.include_router(authentication_router)
app.include_router(expense_router)
app.include_router(budget_router)
app.include_router(agent_router)
app.include_router(admin_router)


@app.get(path="/")
def root() -> dict[str, str]:
    return {"root": "service running"}


@app.get(path="/health")
def get_health() -> dict:
    return {"health": "running", "service": "finance_tracker_api"}
