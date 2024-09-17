from cachetools import TTLCache
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import  FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from stream_fusion.logging_config import logger
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.security.security_api_key import check_api_key
from stream_fusion.version import get_version
from stream_fusion.web.root.config.schemas import ManifestResponse, StaticFileResponse
from stream_fusion.settings import settings

router = APIRouter()

templates = Jinja2Templates(directory="/app/stream_fusion/static")
stream_cache = TTLCache(maxsize=1000, ttl=3600)


@router.get("/")
async def root():
    logger.info("Redirecting to /configure")
    return RedirectResponse(url="/configure")


@router.get("/configure")
@router.get("/{config}/configure")
async def configure(request: Request):
    logger.info("Serving configuration page")
    return templates.TemplateResponse("index.html", {"request": request})


# @router.get("/static/{file_path:path}", response_model=StaticFileResponse)
# async def serve_static(file_path: str):
#     logger.debug(f"Serving static file: {file_path}")
#     return FileResponse(f"/app/stream_fusion/static/{file_path}")


@router.get("/manifest.json")
async def get_manifest():
    logger.info("Serving manifest.json")
    return ManifestResponse(
        id="community.limedrive.streamfusion",
        icon="https://i.imgur.com/q2VSdSp.png",
        version=str(get_version()),
        resources=[
            'catalog',
            {
                'name': 'stream', 
                'types': ['movie', 'series'], 
                'idPrefixes': ['tt']
            }
        ],
        types=["movie", "series"],
        name="StreamFusion" + " (dev)" if settings.develop else "",
        description="StreamFusion enhances Stremio by integrating torrent indexers and debrid services, "
                    "providing access to a vast array of cached torrent sources. This plugin seamlessly bridges "
                    "Stremio with popular indexers and debrid platforms, offering users an expanded content "
                    "library and a smooth streaming experience.",
        catalogs=[
            {
                "type": "movie",
                "id": "latest_movies",
                "name": "Yggflix - Films Récents"
            },
            {
                "type": "movie",
                "id": "recently_added_movies",
                "name": "YGGtorrent - Films Récemment Ajoutés"
            },
            {
                "type": "series",
                "id": "latest_tv_shows",
                "name": "Yggflix - Séries Récentes"
            },
            {
                "type": "series",
                "id": "recently_added_tv_shows",
                "name": "YGGtorrent - Séries Récemment Ajoutées"
            }
        ],
        behaviorHints={
            "configurable": True,
            "configurationRequired": True
        },
        config=[
            {
                "key": "api_key",
                "title": "API Key",
                "type": "text",
                "required": True
            }
        ]
    )

@router.get("/{config}/manifest.json")
async def get_manifest(config: str):
    config = parse_config(config)
    logger.debug(f"Parsed configuration: {config}")

    # api_key = config.get("apiKey")
    # if api_key:
    #     await check_api_key(api_key)
    # else:
    #     logger.warning("API key not found in config.")
    #     raise HTTPException(status_code=401, detail="API key not found in config.")

    yggflix_ctg = config.get("yggflixCtg", True)
    yggtorrent_ctg = config.get("yggtorrentCtg", True)

    catalogs = []

    if yggflix_ctg:
        catalogs.extend([
            {
                "type": "movie",
                "id": "latest_movies",
                "name": "Yggflix"
            },
            {
                "type": "series",
                "id": "latest_tv_shows",
                "name": "Yggflix"
            }
        ])

    if yggtorrent_ctg:
        catalogs.extend([
            {
                "type": "movie",
                "id": "recently_added_movies",
                "name": "YGGtorrent - Récemment Ajoutés"
            },
            {
                "type": "series",
                "id": "recently_added_tv_shows",
                "name": "YGGtorrent - Récemment Ajoutées"
            }
        ])

    logger.info("Serving manifest.json")
    return ManifestResponse(
        id="community.limedrive.streamfusion",
        icon="https://i.imgur.com/q2VSdSp.png",
        version=str(get_version()),
        resources=[
            'catalog',
            {
                'name': 'stream', 
                'types': ['movie', 'series'], 
                'idPrefixes': ['tt']
            }
        ],
        types=["movie", "series"],
        name="StreamFusion" + " (dev)" if settings.develop else "",
        description="StreamFusion enhances Stremio by integrating torrent indexers and debrid services,"
         " providing access to a vast array of cached torrent sources. This plugin seamlessly bridges"
         " Stremio with popular indexers and debrid platforms, offering users an expanded content"
         " library and a smooth streaming experience.",
        catalogs=catalogs,
    )
