from sqlalchemy import BigInteger, String, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from stream_fusion.services.postgresql.base import Base
from datetime import datetime
from typing import Optional, List
import hashlib
import json

from stream_fusion.utils.torrent.torrent_item import TorrentItem

class TorrentItemModel(Base):
    """Model for TorrentItem in PostgreSQL."""

    __tablename__ = "torrent_items"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    raw_title: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Kept as BigInteger
    magnet: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    info_hash: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    link: Mapped[str] = mapped_column(String, nullable=False)
    seeders: Mapped[int] = mapped_column(Integer, nullable=False)
    languages: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    indexer: Mapped[str] = mapped_column(String, nullable=False)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    files: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)  # Kept as JSON
    torrent_download: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    trackers: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    file_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    full_index: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)  # Kept as JSON
    availability: Mapped[bool] = mapped_column(Boolean, default=False)

    parsed_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)

    @staticmethod
    def generate_unique_id(raw_title: str, size: int, indexer: str = "cached") -> str:
        unique_string = f"{raw_title}_{size}_{indexer}"
        full_hash = hashlib.sha256(unique_string.encode()).hexdigest()
        return full_hash[:16]

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = self.generate_unique_id(
                kwargs.get('raw_title', ''),
                self._parse_size(kwargs.get('size', 0)),
                kwargs.get('indexer', 'cached')
            )
        super().__init__(**kwargs)
        current_time = int(datetime.now().timestamp())
        if 'created_at' not in kwargs:
            self.created_at = current_time
        if 'updated_at' not in kwargs:
            self.updated_at = current_time

    @classmethod
    def from_torrent_item(cls, torrent_item: TorrentItem):
        model_dict = {}
        for attr, value in torrent_item.__dict__.items():
            if hasattr(cls, attr):
                if attr == 'size':
                    model_dict[attr] = cls._parse_size(value)
                elif attr in ['files', 'full_index']:
                    model_dict[attr] = cls._parse_json(value)
                elif attr == 'parsed_data':
                    model_dict[attr] = value.model_dump() if value else None
                elif attr == "availability":
                    model_dict[attr] = False
                elif attr == "seeders":
                    model_dict[attr] = int(value) if value else 0
                else:
                    model_dict[attr] = value

        return cls(**model_dict)

    def to_torrent_item(self):
        from RTN.models import ParsedData
        from stream_fusion.utils.torrent.torrent_item import TorrentItem

        torrent_item_dict = {}
        for attr, value in self.__dict__.items():
            if attr not in ['_sa_instance_state', 'created_at', 'updated_at']:
                if attr == 'parsed_data':
                    torrent_item_dict[attr] = ParsedData(**value) if value else None
                else:
                    torrent_item_dict[attr] = value

        # Supprimez les attributs qui ne sont pas dans TorrentItem
        valid_attrs = set(TorrentItem.__init__.__code__.co_varnames)
        torrent_item_dict = {k: v for k, v in torrent_item_dict.items() if k in valid_attrs}

        return TorrentItem(**torrent_item_dict)

    @staticmethod
    def _parse_size(size):
        if isinstance(size, str):
            try:
                return int(size)
            except ValueError:
                return 0
        return size

    @staticmethod
    def _parse_json(value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return value