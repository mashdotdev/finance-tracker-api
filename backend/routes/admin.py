from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import select
from app import AsyncSession, get_session, raise_400_exception
from auth import require_admin
from models import User

router = APIRouter(prefix="/admin", tags=["admin control"])


@router.delete(path="/users/{user_id}", description="admin delete a specific user")
async def admin_delete_user(
    user_id: UUID,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    user = (
        await session.exec(select(User).where(User.id == user_id))
    ).first()

    if not user:
        raise raise_400_exception(detail=f"User with id {user_id} does not exist")

    await session.delete(user)
    await session.commit()

    return {"message": f"User {user_id} deleted successfully"}
