from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    name: str = Field(..., description="Name of the API key")
    never_expire: bool = Field(False, description="If True, the key will never expire")

class APIKeyUpdate(BaseModel):
    """Schema for updating an existing API key."""
    is_active: Optional[bool] = Field(None, description="Whether the API key is active")
    expiration_date: Optional[datetime] = Field(None, description="New expiration date for the API key")
    name: Optional[str] = Field(None, description="New name for the API key")

class APIKeyInDB(BaseModel):
    """Schema for API key data as stored in the database."""
    id: int
    api_key: uuid.UUID
    is_active: bool
    never_expire: bool
    expiration_date: Optional[datetime]
    latest_query_date: Optional[datetime]
    total_queries: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={uuid.UUID: str}
    )

class APIKeyOut(BaseModel):
    """Schema for API key data to be returned to the client."""
    api_key: uuid.UUID
    is_active: bool
    never_expire: bool
    expiration_date: Optional[datetime]
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={uuid.UUID: str}
    )