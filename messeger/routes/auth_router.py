from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request

from messeger.config import get_db, oauth2_scheme, logger, limiter
from messeger.schemes import (
    CorrectLoginResponseScheme,
    LoginScheme,
    RefreshTokenResponseScheme,
    RefreshTokenRequestScheme,
    UserCreateScheme
)
from messeger.services import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_access_token,
    hash_password,
    blacklist_token,
    is_token_blacklisted,
    get_user_by_username,
    create_user,
    get_user_by_id
)

auth_router = APIRouter(prefix="/api/auth", tags=["Users"])
app_logger = logger.bind(name="app")


@auth_router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreateScheme, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = await create_user(
        db,
        username=user.username,
        password_hash=hash_password(user.password)
    )
    return {"detail": "ok"}


@auth_router.post("/login", response_model=CorrectLoginResponseScheme)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginScheme, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, login_data.username)
    if not user or not user.check_password(login_data.password):
        raise HTTPException(401, "Incorrect username or password")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id), str(user.token_version))
    return {
        "access_token": access,
        "refresh_token": refresh
    }


@auth_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    jti = payload["jti"]
    exp = payload["exp"]
    if is_token_blacklisted(jti):
        raise HTTPException(401, "Token revoked")
    blacklist_token(jti=jti, exp=exp)
    return {"detail": "Logged out successfully"}


@auth_router.post("/refresh", response_model=RefreshTokenResponseScheme)
async def refresh(data: RefreshTokenRequestScheme, db: AsyncSession = Depends(get_db)):
    app_logger.debug(f"/refresh: {data}")

    token = data.refresh_token
    payload = decode_refresh_token(token)

    app_logger.debug(f"/refresh: decoded payload: {payload}")

    jti = payload["jti"]

    if is_token_blacklisted(jti):
        raise HTTPException(401, "Token revoked")

    app_logger.debug(f"/refresh: Token in blacklist: {is_token_blacklisted(jti):}")

    user_id = payload["sub"]
    user = await get_user_by_id(db, int(user_id))

    app_logger.debug(f"/refresh: User: {user.username}")

    if not user:
        raise HTTPException(401, "User not found")

    # Единственная проверка версии refresh токена
    app_logger.debug(
        f"/refresh: check: payload['version'] != user.token_version: {payload['version']} - {user.token_version}")

    if int(payload["version"]) != user.token_version:
        raise HTTPException(401, "Token revoked")

    exp = payload["exp"]
    blacklist_token(jti=jti, exp=exp)

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id), str(user.token_version))

    return {
        "access_token": access,
        "refresh_token": refresh
    }
