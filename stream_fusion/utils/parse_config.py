import json

from stream_fusion.utils.string_encoding import decodeb64
from stream_fusion.logging_config import logger

def parse_config(b64config):
    config = json.loads(decodeb64(b64config))

    if "languages" not in config:
        config["languages"] = [config["language"]]
    if "jackett" not in config:
        config["jackett"] = False
    if isinstance(config.get("RDToken"), str):
        try:
            config["RDToken"] = json.loads(config["RDToken"])
        except json.JSONDecodeError:
            pass
    if "anonymizeMagnets" not in config:
        config["anonymizeMagnets"] = False
    return config