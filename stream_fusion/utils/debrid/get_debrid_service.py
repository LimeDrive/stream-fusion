from fastapi.exceptions import HTTPException

from stream_fusion.utils.debrid.alldebrid import AllDebrid
from stream_fusion.utils.debrid.realdebrid import RealDebrid
from stream_fusion.utils.debrid.torbox import Torbox
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings


def get_all_debrid_services(config):
    services = config['service']
    debrid_service = []
    if not services:
        logger.error("No service configuration found in the config file.")
        return
    for service in services:
        if service == "Real-Debrid":
            debrid_service.append(RealDebrid(config))
            logger.debug("Real-Debrid: service added to be use")
        if service == "AllDebrid":
            debrid_service.append(AllDebrid(config))
            logger.debug("AllDebrid: service added to be use")
        if service == "TorBox":
            debrid_service.append(Torbox(config))
            logger.debug("TorBox: service added to be use")
    if not debrid_service:
        raise HTTPException(status_code=500, detail="Invalid service configuration.")
    
    return debrid_service

def get_download_service(config):
    if not settings.download_service:
        service = config['debridDownloader']
    else:
        service = settings.download_service
    if not service:
        logger.error("No download service found in the user config.")
        return
    if service == "RD":
        return RealDebrid(config)
    elif service == "AD":
        return AllDebrid(config)
    elif service == "TB":
        return Torbox(config)
    else:
        logger.error("Invalid service configuration return by stremio in the query.")
        raise HTTPException(status_code=500, detail="Invalid service configuration return by stremio.")


def get_debrid_service(config, service):
    if not service:
        service == settings.download_service
    if service == "RD":
        return RealDebrid(config)
    elif service == "AD":
        return AllDebrid(config)
    elif service == "TB":
        return Torbox(config)
    elif service == "DL":
        return get_download_service(config)
    else:
        logger.error("Invalid service configuration return by stremio in the query.")
        raise HTTPException(status_code=500, detail="Invalid service configuration return by stremio.")
