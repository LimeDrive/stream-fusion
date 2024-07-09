from fastapi.routing import APIRouter

from stream_fusion.web.api import auth, docs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["_auth"])
api_router.include_router(docs.router)