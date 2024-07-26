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
    # Cut the option due to backwards compatibility
    if "jackett" not in config:
        config["jackett"] = False
    if "yggPassword" not in config:
        config["yggPassword"] = "FakePassword"
    if "yggUsername" not in config:
        config["yggUsername"] = "FakeUsername"

    # Break old config on debrid untested
    if config["service"] == "AllDebrid" or "Premiumize":
        raise Exception("Old config detected, please reconfigure")
    return config