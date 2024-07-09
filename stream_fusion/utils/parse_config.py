import json

from stream_fusion.utils.string_encoding import decodeb64


def parse_config(b64config):
    config = json.loads(decodeb64(b64config))

    # For backwards compatibility
    if "languages" not in config:
        config["languages"] = [config["language"]]

    if "anonymizeMagnets" not in config:
        config["anonymizeMagnets"] = False # Default to False if not specified

    return config
