import time

from messeger.config import r


def blacklist_token(jti: str, exp: int):
    """Метод добавления токена в redis"""
    ttl = max(0, int(exp - time.time()))
    r.setex(
        f"auth:blacklist:{jti}",
        ttl,
        "1"
    )


def is_token_blacklisted(jti: str) -> bool:
    """Метод поиска токена в redis"""
    # if is_token_blacklisted(jti):
    #   raise HTTPException(401, "Token revoked")
    return r.exists(f"auth:blacklist:{jti}") == 1
