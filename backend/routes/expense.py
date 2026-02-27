from fastapi import APIRouter, Depends, status
from sqlmodel import select, func
from app import AsyncSession, get_session, raise_400_exception
from auth import get_current_user
from models import Category, Expenses, User, ExpenseCreate

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get(path="", description="get all expenses for current user")
async def get_all_expenses(
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if category:
        category_id = (
            await session.exec(
                select(Category.id).where(
                    func.lower(Category.name) == category.lower(),
                    Category.user_id == current_user.id,
                )
            )
        ).first()

        filtered_expenses = (
            await session.exec(
                select(Expenses).where(
                    Expenses.category_id == category_id,
                    Expenses.user_id == current_user.id,
                )
            )
        ).all()

        return filtered_expenses

    expenses = (
        await session.exec(select(Expenses).where(Expenses.user_id == current_user.id))
    ).all()

    if len(expenses) == 0:
        return {"message": "You dont have any expenses yet"}

    return expenses


@router.post(
    path="/create", description="create an expense", status_code=status.HTTP_201_CREATED
)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Verify the category exists AND belongs to the current user
    category = (
        await session.exec(
            select(Category).where(
                Category.id == expense_data.category_id,
                Category.user_id == current_user.id,
            )
        )
    ).first()

    if not category:
        raise raise_400_exception(
            detail="Category not found. Please select a valid category or create one first."
        )

    expense = Expenses(
        **expense_data.model_dump(),
        user_id=current_user.id,
        owner=current_user,
    )

    session.add(expense)
    await session.commit()
    await session.refresh(expense)

    return expense


@router.get(path="/{id}")
async def get_expense_by_id(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Expenses:
    expense = (
        await session.exec(
            select(Expenses).where(
                Expenses.id == id, Expenses.user_id == current_user.id
            )
        )
    ).first()

    if not expense:
        raise raise_400_exception(detail="This expense does not exists! Create first")

    return expense


@router.delete(path="/{id}")
async def delete_expense(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    expense_exists = (
        await session.exec(
            select(Expenses).where(
                Expenses.id == id, Expenses.user_id == current_user.id
            )
        )
    ).first()
    if not expense_exists:
        raise raise_400_exception(detail="This expense does not exists")

    await session.delete(expense_exists)
    await session.commit()

    return {"message": "Expense deleted successfully"}
