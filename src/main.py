from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy.exc import ArgumentError

from src import backend_pre_start
from src.adapters import orm
from src.api.api_v1.api import api_router
from src.config import settings

backend_pre_start.main()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

try:
    orm.start_mappers()
except ArgumentError:
    pass


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
