from pydantic import BaseModel, Field
from typing import List, Optional

class ManifestResponse(BaseModel):
    id: str
    icon: str
    version: str
    catalogs: List = Field(default_factory=list)
    resources: List[str]
    types: List[str]
    name: str
    description: str
    behaviorHints: dict = Field(default_factory=lambda: {
        "configurable": True,
    })
    config: Optional[List[dict]] = None

class ConfigureTemplateContext(BaseModel):
    request: dict

class StaticFileResponse(BaseModel):
    file_path: str
