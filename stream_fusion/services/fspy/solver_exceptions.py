class UnsupportedProxySchema(Exception):
    pass


class FlareSolverError(Exception):
    def __init__(self, status: str, version: str, message: str):
        super().__init__(message)
        self.status = status
        self.version = version
        self.message: message

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(
            dct["status"],
            dct["version"],
            dct["message"]
        )