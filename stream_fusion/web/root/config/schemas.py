from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ResourceItem(BaseModel):
    name: str
    types: List[str]
    idPrefixes: List[str]

class CatalogItem(BaseModel):
    type: str
    id: str
    name: str

class ManifestResponse(BaseModel):
    id: str
    icon: str
    version: str
    catalogs: List[CatalogItem] = Field(default_factory=list)
    resources: List[Union[str, ResourceItem]]
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