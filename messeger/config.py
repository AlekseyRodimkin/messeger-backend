import os
import sys
import sqlalchemy.orm as so
import redis

from fastapi import FastAPI
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Any
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
Base = so.declarative_base()

# for local
if not find_dotenv():
    exit("Not exists .env")
else:
    load_dotenv()


    def env_bool(name: str, default: bool = False) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.lower() in ("1", "true", "yes", "on")

DEBUG_MODE = env_bool("DEBUG")
LOCAL_MODE = env_bool("LOCAL")

print("!!!!!!!! CONFIG: !!!!!!!!")
print(f"!!!!!!!! DEBUG = {DEBUG_MODE} !!!!!!!!", )
print(f"!!!!!!!! LOCAL = {LOCAL_MODE} !!!!!!!!", )

app = FastAPI()

# slowapi
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# DB
if LOCAL_MODE:
    DB_HOST = os.getenv("POSTGRES_HOST")
else:
    DB_HOST = "127.0.0.1"
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=DEBUG_MODE)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """Creating tables at start"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[Any, Any]:
    """Get DB session"""
    async with async_session() as session:
        yield session


# redis
if LOCAL_MODE:
    REDIS_HOST = os.getenv("REDIS_HOST")
else:
    REDIS_HOST = "localhost"

REDIS_USER = os.getenv("REDIS_USER")
REDIS_USER_PASSWORD = os.getenv("REDIS_USER_PASSWORD")
r = redis.Redis(
    host=REDIS_HOST,
    port=6380,
    username=REDIS_USER,
    password=REDIS_USER_PASSWORD,
    db=0,
    decode_responses=True
)

# Password hash
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY", default=DB_USER + DB_PASSWORD)
ALGORITHM = os.getenv("ALGORITHM", default="HS256")
ISS = os.getenv("ISS")
if DEBUG_MODE:
    ACCESS_TOKEN_EXPIRE_MINUTES = 5
    REFRESH_TOKEN_EXPIRE_DAYS = 1
else:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default=15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", default=7))

# Logs
(BASE_DIR / "logs").mkdir(exist_ok=True)

logger.remove()  # delete default logger

# app config
logger.add(
    sys.stdout,
    level="DEBUG" if DEBUG_MODE else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} - {name} - {line} - {level} - {message}",
    filter=lambda record: record["extra"].get("name", "app") == "app",
    enqueue=True,
)

logger.add(
    str(BASE_DIR / "logs/app_debug.log"),
    level="DEBUG" if DEBUG_MODE else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} - {name} - {line} - {level} - {message}",
    rotation="50 MB",
    retention=5,
    filter=lambda record: record["extra"].get("name", "app") == "app",
    enqueue=True,
)

logger.add(
    str(BASE_DIR / "logs/app_error.log"),
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} - {name} - {line} - {level} - {message}",
    rotation="5 MB",
    retention=5,
    filter=lambda record: record["extra"].get("name", "app") == "app",
    enqueue=True,
)

# tests config
logger.add(
    sys.stdout,
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} - {name} - {line} - {level} - {message}",
    filter=lambda record: record["extra"].get("name") == "tests",
    enqueue=True,
)

logger.add(
    str(BASE_DIR / "logs/tests_debug.log"),
    level="DEBUG" if DEBUG_MODE else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} - {name} - {line} - {level} - {message}",
    rotation="50 MB",
    retention=5,
    filter=lambda record: record["extra"].get("name") == "tests",
    enqueue=True,
)

logger.add(
    str(BASE_DIR / "logs/tests_error.log"),
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} - {name} - {line} - {level} - {message}",
    rotation="5 MB",
    retention=5,
    filter=lambda record: record["extra"].get("name") == "tests",
    enqueue=True,
)
