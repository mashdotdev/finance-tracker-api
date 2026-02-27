from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from datetime import timedelta, datetime
from typing import Optional, Any
from jose import jwt
from jose.exceptions import JWTError
from app import Settings, get_settings

settings: Settings = get_settings()
password_hash = PasswordHash((Argon2Hasher(),))


def encrypt_password(plain_password: str) -> str:
    return password_hash.hash(password=plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(password=plain_password, hash=hashed_password)


def create_jwt_token(data: dict, expires: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    return jwt.encode(
        claims=to_encode, key=settings.secret_key, algorithm=settings.algorithm
    )


def decode_jwt_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token=token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
    except JWTError:
        return None
