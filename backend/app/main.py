from fastapi import FastAPI
from routes import category_router, authentication_router, expense_router, budget_router
from app import lifespan

app = FastAPI(
    title="Smart Finance Tracker API",
    description="AI powered finance tracker api",
    lifespan=lifespan,
)

app.include_router(category_router)
app.include_router(authentication_router)
app.include_router(expense_router)
app.include_router(budget_router)


@app.get(path="/health")
def get_health() -> dict:
    return {"health": "running", "service": "finance_tracker_api"}
