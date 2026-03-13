import uuid

from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from messeger.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ISS


def create_access_token(user_id: str) -> str:
    """
    Функция генерации access токена

    sub (Subject) — собственник токена (uuid пользователя)
    type — тип токена (access / refresh)
    exp (Expiration Time) — время, в течение которого токен считается валидным
    iat (Issued At) — время создания токена
    jti (JWT ID) — уникальный идентификатор токена
    iss (Issuer) — издатель токена
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": iat,
        "jti": str(uuid.uuid4()),
        "iss": ISS
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str, user_token_version: str) -> str:
    """
    Функция генерации refresh токена

    sub (Subject) — собственник токена (uuid пользователя)
    type — тип токена (access / refresh)
    exp (Expiration Time) — время, в течение которого токен считается валидным
    iat (Issued At) — время создания токена
    version - версия токена (из модели пользователя)
    jti (JWT ID) — уникальный идентификатор токена
    iss (Issuer) — издатель токена
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    iat = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": iat,
        "jti": str(uuid.uuid4()),
        "version": user_token_version,
        "iss": ISS
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """
    Метод декодирования access токена

    Выполняет проверки:
    - Exists: sub, jti, type, iss: 401 (Invalid token)
    - SECRET_KEY: JWTError 401 (Invalid token)
    - exp: ExpiredSignatureError 401 (Access token expired)
    - type: 401 (Invalid token type)
    - iss: 401 (Invalid issuer)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(401, "Access token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    jti = payload.get("jti")
    token_type = payload.get("type")
    iss = payload.get("iss")
    if not sub or not jti or not token_type or not iss:
        raise HTTPException(401, "Invalid token")

    if token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    if iss != "messeger-api":
        raise HTTPException(401, "Invalid issuer")

    return payload


def decode_refresh_token(token: str):
    """
    Метод декодирования refresh токена

    Выполняет проверки:
    - Exists: sub, jti, type, iss: 401 (Invalid token)
    - SECRET_KEY: JWTError 401 (Invalid token)
    - exp: ExpiredSignatureError 401 (Refresh token expired)
    - type: 401 (Invalid token type)
    - iss: 401 (Invalid issuer)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(401, "Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    jti = payload.get("jti")
    token_type = payload.get("type")
    iss = payload.get("iss")
    version = payload.get("version")
    if not sub or not jti or not token_type or not iss or not version:
        raise HTTPException(401, "Invalid token")

    if token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    if iss != "messeger-api":
        raise HTTPException(401, "Invalid issuer")

    return payload
