import json

from stream_fusion.utils.string_encoding import decodeb64


def parse_config(b64config):
    config = json.loads(decodeb64(b64config))

    if "languages" not in config:
        config["languages"] = [config["language"]]
    if isinstance(config.get("debridKey"), str):
        try:
            config["debridKey"] = json.loads(config["debridKey"])
        except json.JSONDecodeError:
            pass
    if "anonymizeMagnets" not in config:
        config["anonymizeMagnets"] = False
    return config