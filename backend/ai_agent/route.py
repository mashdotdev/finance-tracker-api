from fastapi import APIRouter
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel
from app import Settings, get_settings

set_tracing_disabled(True)
router = APIRouter(prefix="/agent", tags=["agent"])
settings: Settings = get_settings()

external_client = AsyncOpenAI(
    api_key=settings.gemini_api_key, base_url=settings.gemini_base_url
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash", openai_client=external_client
)


class AgentRequest(BaseModel):
    message: str


@router.post(path="/chat", description="Chat wit the finance AI Agent")
async def chat(request: AgentRequest):
    agent = Agent(name="Smart Agent", instructions="You are a smart agent", model=model)

    result = await Runner.run(starting_agent=agent, input=request.message)

    return {"agent_response": result.final_output}
