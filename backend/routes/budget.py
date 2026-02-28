from fastapi import APIRouter, Depends
from sqlmodel import select, func, col
from datetime import datetime
from app import get_session, AsyncSession, raise_400_exception
from models import Budget, User, BudgetCreate, Category, Expenses
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


@router.post(path="/create", description="set monthly budget per category")
async def set_monthly_budget(
    budget_create: BudgetCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    category = (
        await session.exec(
            select(Category).where(
                Category.id == budget_create.category_id,
                Category.user_id == current_user.id,
            )
        )
    ).first()
    if not category:
        raise raise_400_exception(
            detail="Category not found. Please select a valid category or create one first."
        )

    budget_exists = (
        await session.exec(
            select(Budget).where(
                Budget.category_id == budget_create.category_id,
                Budget.user_id == current_user.id,
            )
        )
    ).first()
    if budget_exists:
        raise raise_400_exception(
            detail="A budget for this category already exists. Update it instead."
        )

    budget = Budget(
        **budget_create.model_dump(), user_id=current_user.id, owner=current_user
    )

    session.add(budget)
    await session.commit()
    await session.refresh(budget)

    return {
        "id": budget.id,
        "budget": budget.monthly_limit,
        "category_id": budget.category_id,
    }


@router.put(path="/update/{budget_id}", description="update the budget for category")
async def update_budget(
    budget_id: str,
    new_monthly_limit: float,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    budget_exists = (
        await session.exec(
            select(Budget).where(
                Budget.id == budget_id, Budget.user_id == current_user.id
            )
        )
    ).first()
    if not budget_exists:
        raise raise_400_exception(detail="Budget does not exists")

    budget_exists.monthly_limit = new_monthly_limit

    session.add(budget_exists)
    await session.commit()
    await session.refresh(budget_exists)

    return {"new_budget": budget_exists.monthly_limit}


@router.get(
    path="/summary",
    description="get summary by total spending - budget for the current month",
)
async def get_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    now = datetime.now()

    budgets = (
        await session.exec(select(Budget).where(Budget.user_id == current_user.id))
    ).all()

    if not budgets:
        return {"message": "No budgets set. Create a budget first."}

    summary = []
    for budget in budgets:
        spent = (
            await session.exec(
                select(func.sum(Expenses.amount)).where(
                    Expenses.category_id == budget.category_id,
                    Expenses.user_id == current_user.id,
                    func.extract("month", col(Expenses.date)) == now.month,
                    func.extract("year", col(Expenses.date)) == now.year,
                )
            )
        ).one()

        total_spent = spent or 0.0
        summary.append(
            {
                "category_id": budget.category_id,
                "monthly_limit": budget.monthly_limit,
                "spent": total_spent,
                "remaining": budget.monthly_limit - total_spent,
            }
        )

    return summary
