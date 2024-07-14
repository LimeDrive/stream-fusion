import json

from stream_fusion.utils.string_encoding import decodeb64


def parse_config(b64config):
    config = json.loads(decodeb64(b64config))

    # For backwards compatibility
    if "languages" not in config:
        config["languages"] = [config["language"]]
    # Cut the option due to backwards compatibility
    if "anonymizeMagnets" not in config:
        config["anonymizeMagnets"] = False
    return config