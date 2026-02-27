from fastapi import FastAPI


app = FastAPI(
    title="Smart Finance Tracker API", description="AI powered finance tracker api"
)


@app.get(path="/health")
def get_health() -> dict:
    return {"health": "running", "service": "finance_tracker_api"}
