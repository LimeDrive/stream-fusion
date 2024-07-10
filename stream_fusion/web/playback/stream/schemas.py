from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

class HeadResponse(BaseModel):
    status_code: int