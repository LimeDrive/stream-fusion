from fastapi.routing import APIRouter

from stream_fusion.web.playback import stream

stream_router = APIRouter()
stream_router.include_router(stream.router, prefix="/playback", tags=["stream"])