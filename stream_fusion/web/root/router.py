from fastapi.routing import APIRouter

from stream_fusion.web.root import config
from stream_fusion.web.root import search
from stream_fusion.web.root import catalog

root_router = APIRouter()
root_router.include_router(config.router, tags=["config"])
root_router.include_router(search.router, tags=["search"])
root_router.include_router(catalog.router, tags=["catalog"])