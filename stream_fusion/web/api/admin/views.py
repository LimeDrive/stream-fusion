from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import secrets

from stream_fusion.utils.security.security_secret import GhostLoadedSecret
from stream_fusion.services.security_db import security_db_access
from stream_fusion.web.api.auth.schemas import UsageLogs
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings

router = APIRouter()

templates = Jinja2Templates(directory="/app/stream_fusion/static/admin")

SECRET_KEY_NAME = "secret-key"
secret_header = APIKeyHeader(name=SECRET_KEY_NAME, auto_error=False)

secret = GhostLoadedSecret()

def custom_url_for(name: str, **path_params: any) -> str:
    def wrapper(request: Request):
        url = request.url_for(name, **path_params)
        if settings.use_https:
            return str(url.replace(scheme="https"))
        return str(url)
    return wrapper

templates.env.globals["url_for"] = custom_url_for

async def get_secret_key_from_session(request: Request):
    secret_key = request.session.get("secret_key")
    if not secret_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Session expirée ou invalide")
    return secret_key

async def session_based_security(secret_key: str = Depends(get_secret_key_from_session)):
    if not secrets.compare_digest(secret_key, secret.value):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Clé secrète invalide"
        )
    return True

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, secret_key: str = Form(...)):
    if secrets.compare_digest(secret_key, secret.value):
        request.session["secret_key"] = secret_key
        return RedirectResponse(url=custom_url_for("list_api_keys")(request), status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Clé secrète invalide"})

@router.get("/api-keys", response_class=HTMLResponse, dependencies=[Depends(session_based_security)])
async def list_api_keys(request: Request):
    logs = security_db_access.get_usage_stats()
    usage_logs = UsageLogs(logs=[
        {
            "api_key": row[0],
            "is_active": row[1],
            "never_expire": row[2],
            "expiration_date": row[3] if row[3] is not None else "Illimited",
            "latest_query_date": row[4] if row[4] is not None else "None",
            "total_queries": row[5],
            "name": row[6] if row[6] is not None else "JhonDo"
        } for row in logs
    ])
    return templates.TemplateResponse("api_keys.html", {"request": request, "logs": usage_logs.logs})

@router.get("/create-api-key", response_class=HTMLResponse, dependencies=[Depends(session_based_security)])
async def create_api_key_page(request: Request):
    return templates.TemplateResponse("create_api_key.html", {"request": request})

@router.post("/create-api-key", dependencies=[Depends(session_based_security)])
async def create_api_key(request: Request, name: str = Form(None), never_expires: bool = Form(False)):
    new_key = security_db_access.create_key(name, never_expires)
    return RedirectResponse(url=custom_url_for("list_api_keys")(request), status_code=303)

@router.post("/revoke-api-key", dependencies=[Depends(session_based_security)])
async def revoke_api_key(request: Request, api_key: str = Form(...)):
    security_db_access.revoke_key(api_key)
    return RedirectResponse(url=custom_url_for("list_api_keys")(request), status_code=303)

@router.post("/renew-api-key", dependencies=[Depends(session_based_security)])
async def renew_api_key(request: Request, api_key: str = Form(...)):
    security_db_access.renew_key(api_key)
    return RedirectResponse(url=custom_url_for("list_api_keys")(request), status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url=custom_url_for("login_page")(request), status_code=303)