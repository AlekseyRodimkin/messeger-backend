import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from messeger.app import app
from messeger.config import Base, get_db, logger

tests_logger = logger.bind(name="tests")

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

test_data = {
    "username": "testuser",
    "password": "123456789A!"
}


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Создает и удаляет таблицы перед каждым тестом."""
    tests_logger.debug("db_session()")
    async with test_engine.begin() as conn:
        tests_logger.debug("Create tables ...")
        await conn.run_sync(Base.metadata.create_all)
        tests_logger.debug("Tables created")

        async with AsyncSession(test_engine) as session:
            yield session

        tests_logger.debug("Delete tables ...")
        await conn.run_sync(Base.metadata.drop_all)
        tests_logger.debug("Tables deleted")


@pytest_asyncio.fixture(scope="function")
def test_client(db_session):
    """Фикстура для тестового клиента с тестовой БД и фиктивным пользователем"""

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    # async def override_get_current_user(token: str = Depends(lambda: test_user["token"])):
    #     token_hashed = hash_token(token)
    #     result = await db_session.execute(
    #         sa.select(Token).where(
    #             Token.token_hash == token_hashed,
    #             Token.expires_at > datetime.now(timezone.utc)
    #         )
    #     )
    #     db_token = result.scalars().first()
    #     if not db_token:
    #         raise HTTPException(status_code=401, detail="Invalid or expired token")
    #
    #     result = await db_session.execute(sa.select(User).where(User.id == db_token.user_id))
    #     user = result.scalars().first()
    #     if not user:
    #         raise HTTPException(status_code=401, detail="User not found")
    #     return user

    # переопределяем зависимости
    app.dependency_overrides[get_db] = override_get_db
    # app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    # чистим после теста
    app.dependency_overrides.clear()
