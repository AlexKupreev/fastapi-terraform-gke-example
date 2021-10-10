from fastapi import APIRouter

from src.api.api_v1.endpoints import items, login, users, utils, basic_utils


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(
    basic_utils.router, prefix="/basic_utils", tags=["basic_http"]
)


@api_router.get("/healthz")
def healthcheck():
    return {"msg": "OK"}
