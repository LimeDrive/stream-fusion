from sqlalchemy.orm import DeclarativeBase

from stream_fusion.services.postgresql.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
