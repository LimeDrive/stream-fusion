from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Boolean, DateTime
from stream_fusion.services.postgresql.base import Base
from datetime import datetime
from typing import Optional
import uuid

class APIKeyModel(Base):
    """Model for API Keys using UUID4."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, index=True, nullable=False, default=uuid.uuid4)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    never_expire: Mapped[bool] = mapped_column(Boolean, default=False)
    expiration_date: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    latest_query_date: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_queries: Mapped[int] = mapped_column(default=0)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'api_key' not in kwargs:
            self.api_key = uuid.uuid4()
