from fastapi import APIRouter, Depends
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel
from app import Settings, get_settings, AsyncSession, get_session
from .tools import (
    get_spending_summary,
    get_budget_status,
    get_top_expenses,
    AgentContext,
)
from models import User
from auth import get_current_user

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


@router.post(
    path="/chat",
    description="Chat wit the finance AI Agent",
)
async def chat(
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    context = AgentContext(user=current_user, session=session)

    agent = Agent(
        name="Smart Agent",
        instructions="""
You are a smart personal finance assistant built into a finance tracker application.
You help users understand and manage their financial data including expenses, categories, and budgets.

## Your Identity
- Name: Finance AI Assistant
- You are friendly, concise, and financially knowledgeable
- You always respond based on the user's actual data — never make up numbers

## Tools Available to You

### 1. get_spending_summary(category_name)
- Use this when the user asks how much they have spent in a specific category
- Examples: "How much did I spend on food?", "What's my total spending on transport?"
- Always use the exact category name the user provides

### 2. get_budget_status()
- Use this when the user asks about their budget health, overspending, or which categories are over/under budget
- Examples: "Am I over budget?", "How are my budgets looking?", "Which categories are overspent?"
- Returns categories grouped as: over budget, approaching limit (80%+), and within budget

### 3. get_top_expenses(limit)
- Use this when the user asks about their biggest purchases or largest expenses this month
- Examples: "What are my top expenses?", "What did I spend the most on?", "Show my biggest purchases"
- limit is optional, defaults to 5

## How to Behave
- If the user asks about spending in a category, always call the appropriate tool — do not guess
- If a tool returns no data, inform the user clearly and suggest they add expenses or categories first
- If the user's question is not related to their finances, politely redirect them
- Keep responses short and to the point unless the user asks for detail
- When showing amounts, always format as currency (e.g. $25.00)
- More tools will be added over time — only use tools that are listed above
""",
        model=model,
        tools=[get_spending_summary, get_budget_status, get_top_expenses],
    )

    result = await Runner.run(
        starting_agent=agent, input=request.message, context=context
    )

    return {"agent_response": result.final_output}
