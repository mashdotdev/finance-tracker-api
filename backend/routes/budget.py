from fastapi import APIRouter, Depends
from sqlmodel import select
from app import get_session, AsyncSession
from models import Budget, User
from auth import get_current_user

router = APIRouter(prefix="/budget", tags=["budgets"])


@router.get(path="", description="get all budget limits")
async def get_budgets(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    budgets = (
        await session.exec(select(Budget).where(Budget.user_id == current_user.id))
    ).all()

    if len(budgets) == 0:
        return {"message": "You dont have any budget set"}

    return budgets
