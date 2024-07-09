from fastapi.routing import APIRouter

from stream_fusion.web.root import config
from stream_fusion.web.root import search

root_router = APIRouter()
root_router.include_router(config.router, tags=["config"])
root_router.include_router(search.router, tags=["search"])