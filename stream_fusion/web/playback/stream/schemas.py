from pydantic import BaseModel

class StreamResponse(BaseModel):
    content_range: str | None
    content_length: str | None
    accept_ranges: str
    content_type: str

class ErrorResponse(BaseModel):
    detail: str

class HeadResponse(BaseModel):
    status_code: int