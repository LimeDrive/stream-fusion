from uuid import UUID
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery
from starlette.status import HTTP_403_FORBIDDEN
from stream_fusion.services.postgresql.dao.apikey_dao import APIKeyDAO
from stream_fusion.logging_config import logger

API_KEY_NAME = "api-key"
api_key_query = APIKeyQuery(
    name=API_KEY_NAME, scheme_name="API key query", auto_error=False
)
api_key_header = APIKeyHeader(
    name=API_KEY_NAME, scheme_name="API key header", auto_error=False
)


async def api_key_security(
    apikey_dao: APIKeyDAO,
    query_param: str = Security(api_key_query),
    header_param: str = Security(api_key_header),
):
    if not query_param and not header_param:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="An API key must be passed as query or header",
        )

    api_key = query_param or header_param
    is_valid = await apikey_dao.check_key(api_key)

    if not is_valid:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Wrong, revoked, or expired API key.",
        )

    return api_key


async def check_api_key(api_key: str, apikey_dao: APIKeyDAO):
    try:
        api_key_uuid = UUID(api_key)
    except ValueError:
        logger.error(f"Invalid API key format: {api_key}")
        raise HTTPException(status_code=400, detail="Invalid API key format")
    is_valid = await apikey_dao.check_key(api_key_uuid)
    if not is_valid:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Wrong, revoked, or expired API key.",
        )
