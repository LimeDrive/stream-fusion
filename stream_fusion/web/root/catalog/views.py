import asyncio
import pickle

from redis import Redis
from tmdbv3api import TMDb, Movie, TV, Season
from fastapi_simple_rate_limiter import rate_limiter
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_simple_rate_limiter.database import create_redis_session

from stream_fusion.settings import settings
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.security.security_api_key import check_api_key
from stream_fusion.utils.yggfilx.yggflix_api import YggflixAPI
from stream_fusion.web.root.catalog.schemas import ErrorResponse, Metas, Meta, Video
from stream_fusion.services.redis.redis_config import get_redis
from stream_fusion.logging_config import logger

router = APIRouter()

redis_session = create_redis_session(host=settings.redis_host, port=settings.redis_port)

tmdb = TMDb()
tmdb.api_key = settings.tmdb_api_key
tmdb.language = "fr-FR"
movie = Movie()
tv = TV()
season = Season()


async def get_movie_details(tmdb_id):
    return await asyncio.to_thread(movie.details, tmdb_id)


async def get_tv_details(tmdb_id):
    return await asyncio.to_thread(tv.details, tmdb_id)


async def get_tv_season_details(tmdb_id, season_number):
    return await asyncio.to_thread(season.details, tmdb_id, season_number)


@router.get("/{config}/catalog/{type}/{id}.json", responses={500: {"model": ErrorResponse}})
@rate_limiter(limit=20, seconds=60, redis=redis_session)
async def get_catalog(
    config: str,
    type: str,
    id: str,
    request: Request,
    redis_client: Redis = Depends(get_redis),
):
    try:
        config = parse_config(config)
        logger.debug(f"Parsed configuration: {config}")
        api_key = config.get("apiKey")
        if api_key:
            await check_api_key(api_key)
        else:
            logger.warning("API key not found in config.")
            raise HTTPException(status_code=401, detail="API key not found in config.")

        logger.debug(
            f"Received catalog request from api_key: {api_key}, type: {type}, id: {id}"
        )

        # Validate type and id
        valid_types = {"movie", "series"}
        valid_ids = {"latest_movies", "recently_added_movies", "latest_tv_shows", "recently_added_tv_shows"}
        
        if type not in valid_types:
            raise HTTPException(status_code=400, detail="Invalid type")
        if id not in valid_ids:
            raise HTTPException(status_code=400, detail="Invalid catalog id")
        
        # Check if the type matches the id
        if (type == "movie" and "tv_shows" in id) or (type == "series" and "movies" in id):
            raise HTTPException(status_code=400, detail="Type and catalog id mismatch")

        cache_key = f"yggflix_catalog:{type}:{id}"
        cached_catalog = await asyncio.to_thread(redis_client.get, cache_key)
        if cached_catalog:
            logger.info(f"Catalog found in cache for key: {cache_key}")
            return Metas.model_validate(pickle.loads(cached_catalog))

        # If not in cache, build the catalog
        yggflix = YggflixAPI()
        home_data = await asyncio.to_thread(yggflix.get_home)

        metas = []
        pipeline = redis_client.pipeline()
        
        # Only process the requested catalog
        for item in home_data[id]:
            tmdb_id = item["id"]

            item_cache_key = f"tmdbid_item:{tmdb_id}"
            cached_item = await asyncio.to_thread(redis_client.get, item_cache_key)
            if cached_item:
                try:
                    meta = Meta.model_validate(pickle.loads(cached_item))
                    metas.append(meta)
                except Exception as ve:
                    logger.warning(f"Validation error for cached item {tmdb_id}: {ve}")
                    await asyncio.to_thread(redis_client.delete, item_cache_key)
                continue
            
            try:
                # If not in cache, get details from TMDB
                if type == "movie":
                    details = await get_movie_details(tmdb_id)
                    item_type = "movie"
                    imdb_id = details.imdb_id
                else:
                    details = await get_tv_details(tmdb_id)
                    item_type = "series"
                    # For TV shows, we need to get the IMDb ID from external IDs
                    external_ids = await asyncio.to_thread(tv.external_ids, tmdb_id)
                    imdb_id = external_ids.get("imdb_id")

                if not imdb_id:
                    logger.warning(f"No IMDb ID found for TMDB ID: {tmdb_id}")
                    continue  # Skip this item if no IMDb ID is found

                logger.debug(f"Details for TMDB ID {tmdb_id}: {details}")

                def extract_year(date_string):
                    if date_string and len(date_string) >= 4:
                        return date_string[:4]
                    return None

                # Création de l'objet Meta
                meta = Meta(
                    _id=imdb_id,
                    title=details.title if hasattr(details, "title") else details.name,
                    type=item_type,
                    poster=f"https://image.tmdb.org/t/p/w500{details.poster_path}" if details.poster_path else None,
                    background=f"https://image.tmdb.org/t/p/original{details.backdrop_path}" if details.backdrop_path else None,
                    videos=[],  # Nous allons remplir cela plus tard si nécessaire
                    country=details.production_countries[0].name if details.production_countries else None,
                    tv_language=details.original_language,
                    logo=None,  # TMDB ne fournit pas de logo
                    genres=[genre.name for genre in details.genres] if details.genres else None,
                    description=details.overview,
                    runtime=str(details.runtime) if item_type == "movie" and details.runtime else None,
                    website=details.homepage,
                    imdb_rating=str(details.vote_average) if details.vote_average else None,
                    year=extract_year(details.release_date if item_type == "movie" else details.first_air_date)
                )

                # Si c'est une série TV, ajoutons les informations sur les épisodes
                if item_type == "series" and hasattr(details, 'seasons'):
                    meta.videos = []
                    for season in details.seasons:
                        season_details = await get_tv_season_details(tmdb_id, season.season_number)
                        for episode in season_details.episodes:
                            meta.videos.append(Video(
                                id=str(episode.id),
                                title=episode.name,
                                released=str(episode.air_date),
                                season=season.season_number,
                                episode=episode.episode_number
                            ))

                metas.append(meta)

                # Add the item to the Redis pipeline for a long duration (e.g., 1 day)
                pipeline.set(item_cache_key, pickle.dumps(meta), ex=86400)

            except Exception as e:
                logger.error(f"Error processing item with TMDB ID {tmdb_id}: {str(e)}")
                continue  # Skip this item and continue with the next one

        # Execute the Redis pipeline
        await asyncio.to_thread(pipeline.execute)

        catalog = Metas(metas=metas)

        # Store the complete catalog in Redis for 30 minutes
        await asyncio.to_thread(
            redis_client.set, cache_key, pickle.dumps(catalog), ex=1800
        )

        logger.info(f"Catalog generated and cached for key: {cache_key}")
        return catalog

    except Exception as e:
        logger.error(f"Catalog error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the request."
        )