import sqlalchemy as sa
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from messeger.config import oauth2_scheme, get_db
from messeger.models import User
from messeger.services import is_token_blacklisted, decode_access_token


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    try:
        result = await db.execute(sa.select(User).where(User.username == username))
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    try:
        return await db.get(User, user_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")


async def create_user(db: AsyncSession, username: str, password_hash: str) -> User:
    try:
        user = User(username=username, password_hash=password_hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Username already exists")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=503, detail="Database unavailable")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User | None:
    payload = decode_access_token(token)
    jti = payload["jti"]

    if is_token_blacklisted(jti):
        raise HTTPException(401, "Token revoked")

    user_id = payload["sub"]
    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(401, "User not found")

    return user
