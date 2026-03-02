from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from app import AsyncSession, get_session, credential_exception
from auth import decode_jwt_token
from models import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    payload = decode_jwt_token(token=token)
    if not payload:
        raise credential_exception()

    email: str | None = payload.get("sub")
    if not email:
        raise credential_exception()

    user = (await session.exec(select(User).where(User.email == email))).first()
    if not user:
        raise credential_exception()

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this route",
        )
    return current_user
