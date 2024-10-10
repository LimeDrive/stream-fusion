from typing import List, Optional
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from stream_fusion.services.postgresql.dependencies import get_db_session
from stream_fusion.services.postgresql.models.torrentitem_model import TorrentItemModel
from stream_fusion.logging_config import logger
from stream_fusion.utils.torrent.torrent_item import TorrentItem

class TorrentItemDAO:
    """Class for accessing TorrentItem table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_torrent_item(self, torrent_item: TorrentItem, id: str) -> TorrentItemModel:
        async with self.session.begin():
            try:
                new_item = TorrentItemModel.from_torrent_item(torrent_item)
                new_item.id = id
                self.session.add(new_item)
                await self.session.flush()
                await self.session.refresh(new_item)

                logger.debug(f"TorrentItemDAO: Created new TorrentItem: {new_item.id}")
                return new_item
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error creating TorrentItem: {str(e)}")

    async def get_all_torrent_items(self, limit: int, offset: int) -> List[TorrentItemModel]:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).limit(limit).offset(offset)
                result = await self.session.execute(query)
                items = result.scalars().all()
                logger.debug(f"TorrentItemDAO: Retrieved {len(items)} TorrentItems")
                return items
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error retrieving TorrentItems: {str(e)}")

    async def get_torrent_item_by_id(self, item_id: str) -> Optional[TorrentItemModel]:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.id == item_id)
                result = await self.session.execute(query)
                db_item = result.scalar_one_or_none()
                if db_item:
                    logger.debug(f"TorrentItemDAO: Retrieved TorrentItem: {item_id}")
                    return db_item
                else:
                    logger.debug(f"TorrentItemDAO: TorrentItem not found: {item_id}")
                    return None
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error retrieving TorrentItem {item_id}: {str(e)}")
                return None

    async def update_torrent_item(self, item_id: str, torrent_item: TorrentItem) -> TorrentItemModel:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.id == item_id)
                result = await self.session.execute(query)
                db_item = result.scalar_one_or_none()

                if not db_item:
                    logger.warning(f"TorrentItemDAO: TorrentItem not found for update: {item_id}")
                    return None

                # Update fields
                for key, value in torrent_item.__dict__.items():
                    setattr(db_item, key, value)

                db_item.updated_at = int(datetime.now(timezone.utc).timestamp())
                await self.session.flush()
                await self.session.refresh(db_item)

                logger.debug(f"TorrentItemDAO: Updated TorrentItem: {item_id}")
                return db_item
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error updating TorrentItem {item_id}: {str(e)}")
                return None

    async def delete_torrent_item(self, item_id: str) -> bool:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.id == item_id)
                result = await self.session.execute(query)
                db_item = result.scalar_one_or_none()

                if db_item:
                    await self.session.delete(db_item)
                    logger.debug(f"TorrentItemDAO: Deleted TorrentItem: {item_id}")
                    return True
                else:
                    logger.warning(f"TorrentItemDAO: TorrentItem not found for deletion: {item_id}")
                    return False
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error deleting TorrentItem {item_id}: {str(e)}")
                return False

    async def get_torrent_items_by_info_hash(self, info_hash: str) -> List[TorrentItemModel]:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.info_hash == info_hash)
                result = await self.session.execute(query)
                items = result.scalars().all()
                logger.debug(f"TorrentItemDAO: Retrieved {len(items)} TorrentItems with info_hash: {info_hash}")
                return items
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error retrieving TorrentItems by info_hash {info_hash}: {str(e)}")
                return None
            
    async def get_torrent_items_by_indexer(self, indexer: str) -> List[TorrentItemModel]:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.indexer == indexer)
                result = await self.session.execute(query)
                items = result.scalars().all()
                logger.debug(f"TorrentItemDAO: Retrieved {len(items)} TorrentItems from indexer: {indexer}")
                return items
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error retrieving TorrentItems by indexer {indexer}: {str(e)}")
                return None
            
    async def is_torrent_item_cached(self, item_id: str) -> bool:
        async with self.session.begin():
            try:
                query = select(func.count()).where(TorrentItemModel.id == item_id)
                result = await self.session.execute(query)
                count = result.scalar_one()
                is_cached = count > 0
                logger.debug(f"TorrentItemDAO: TorrentItem {item_id} {'is' if is_cached else 'is not'} in cache")
                return is_cached
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error checking if TorrentItem {item_id} is cached: {str(e)}")
                return None

    async def get_torrent_items_by_type(self, item_type: str) -> List[TorrentItemModel]:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.type == item_type)
                result = await self.session.execute(query)
                items = result.scalars().all()
                logger.debug(f"TorrentItemDAO: Retrieved {len(items)} TorrentItems of type: {item_type}")
                return items
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error retrieving TorrentItems by type {item_type}: {str(e)}")
                return None

    async def get_torrent_items_by_availability(self, available: bool) -> List[TorrentItemModel]:
        async with self.session.begin():
            try:
                query = select(TorrentItemModel).where(TorrentItemModel.availability == available)
                result = await self.session.execute(query)
                items = result.scalars().all()
                logger.debug(f"TorrentItemDAO: Retrieved {len(items)} TorrentItems with availability: {available}")
                return items
            except Exception as e:
                logger.error(f"TorrentItemDAO: Error retrieving TorrentItems by availability {available}: {str(e)}")
                return None