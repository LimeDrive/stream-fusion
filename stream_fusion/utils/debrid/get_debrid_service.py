from fastapi.exceptions import HTTPException

from stream_fusion.utils.debrid.alldebrid import AllDebrid
from stream_fusion.utils.debrid.realdebrid import RealDebrid
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
            logger.debug("Real Debrid service added to be use")
        if service == "AllDebrid":
            debrid_service.append(AllDebrid(config))
            logger.debug("All Debrid service added to be use")
    if not debrid_service:
        raise HTTPException(status_code=500, detail="Invalid service configuration.")
    
    return debrid_service


def get_debrid_service(config, service):
    if not service:
        service == settings.default_debrid_service
    if service == "RD":
        return RealDebrid(config)
    elif service == "AD":
        return AllDebrid(config)
    else:
        logger.error("Invalid service configuration return by stremio in the query.")
        raise HTTPException(status_code=500, detail="Invalid service configuration return by stremio.")
