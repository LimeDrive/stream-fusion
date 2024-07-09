from pydantic import BaseModel, Field
from typing import List, Optional

class Stream(BaseModel):
    name: str
    description: str
    url: Optional[str] = None
    infoHash: Optional[str] = None
    fileIdx: Optional[int] = None
    behaviorHints: dict = Field(default_factory=dict)

class SearchResponse(BaseModel):
    streams: List[Stream]