import toml
from stream_fusion.settings import settings


def get_version():
    with open(settings.version_path, "r") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["tool"]["poetry"]["version"]


if __name__ == "__main__":
    pass