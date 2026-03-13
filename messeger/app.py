from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from .config import engine, app, logger
from . import models
from .routes import user_router, auth_router

app_logger = logger.bind(name="app")

@app.on_event("startup")
async def startup():
    """Function before launching the app (create tables)"""
    app_logger.debug("🔝 App is started 🔝")

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        app_logger.debug("🔄 Tables are created 🔄")


@app.on_event("shutdown")
async def shutdown():
    """Function before the end of the application (close connection, session)"""
    app_logger.debug("⤵️ App is stopped ⤵️")
    await engine.dispose()


# origins = [
#     "http://localhost:3000",
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)


# slowapi
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )
