from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel


class UsageLog(BaseModel):
    api_key: uuid.UUID
    name: Optional[str]
    is_active: bool
    never_expire: bool
    expiration_date: datetime | str | None
    latest_query_date: Optional[datetime] | str | None
    total_queries: int


class UsageLogs(BaseModel):
    logs: list[UsageLog]
