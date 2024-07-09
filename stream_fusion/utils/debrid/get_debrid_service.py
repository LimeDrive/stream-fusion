from fastapi.exceptions import HTTPException

from stream_fusion.utils.debrid.alldebrid import AllDebrid
from stream_fusion.utils.debrid.premiumize import Premiumize
from stream_fusion.utils.debrid.realdebrid import RealDebrid


def get_debrid_service(config):
    service_name = config['service']
    if service_name == "realdebrid":
        debrid_service = RealDebrid(config)
    elif service_name == "alldebrid":
        debrid_service = AllDebrid(config)
    elif service_name == "premiumize":
        debrid_service = Premiumize(config)
    else:
        raise HTTPException(status_code=500, detail="Invalid service configuration.")

    return debrid_service
