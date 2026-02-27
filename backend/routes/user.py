from fastapi import APIRouter, Depends, status
from sqlmodel import select
from app import get_session, AsyncSession
from models import User, UserCreate
from app import raise_400_exception, get_settings, Settings
from auth import encrypt_password, verify_password, create_jwt_token, get_current_user
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from datetime import timedelta

settings: Settings = get_settings()
router = APIRouter(prefix="/users", tags=["authentication"])


@router.post(
    path="/create", description="create a user", status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
):
    user_exists = (
        await session.exec(select(User).where(User.email == user_data.email))
    ).first()
    if user_exists:
        raise raise_400_exception(detail="User with this email already exists")

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=encrypt_password(plain_password=user_data.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"id": user.id, "email": user.email}


@router.post(path="/token", description="sign in user")
async def sign_in(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """check if the user exists and validate credentials"""
    user = (
        await session.exec(select(User).where(User.email == form_data.username))
    ).first()
    if not user or not verify_password(
        plain_password=form_data.password, hashed_password=user.hashed_password
    ):
        raise raise_400_exception(detail="Invalid Credentials")

    "sign jwt token"
    access_token = create_jwt_token(
        data={"sub": user.email}, expires=timedelta(minutes=settings.token_expire_time)
    )

    return {"access_token": access_token, "type": "Bearer"}


@router.get(path="/me", description="current user data")
def read_user_data(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
