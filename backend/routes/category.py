from fastapi import APIRouter, Depends, status
from sqlmodel import select
from uuid import UUID
from app import get_session, AsyncSession, raise_400_exception
from models import Category, CategoryCreate, User
from auth import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(path="", description="get all categories by current user")
async def get_categories(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    categories = (
        await session.exec(select(Category).where(Category.user_id == current_user.id))
    ).all()

    if len(categories) == 0:
        return {"message": "You dont have any category created yet"}

    return categories


@router.post(
    path="/create", description="create a category", status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    category_exist = (
        await session.exec(
            select(Category).where(
                Category.name == category_data.name, Category.user_id == current_user.id
            )
        )
    ).first()
    if category_exist:
        raise raise_400_exception(detail="Category with this name already exists!")

    category = Category(
        name=category_data.name, user_id=current_user.id, owner=current_user
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return {"id": str(category.id), "name": category.name}


@router.delete(path="/{id}", description="delete a category by id")
async def delete_category(
    id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    category_exists = (
        await session.exec(
            select(Category).where(
                Category.id == id, Category.user_id == current_user.id
            )
        )
    ).first()
    if not category_exists:
        raise raise_400_exception(detail=f"Category with this id {id} does not exists")

    await session.delete(category_exists)
    await session.commit()

    return {"message": f"Category {id} deleted successfully"}
