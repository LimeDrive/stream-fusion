import uuid

from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from stream_fusion.services.postgresql.dependencies import get_db_session
from stream_fusion.services.postgresql.models.apikey_model import APIKeyModel
from stream_fusion.logging_config import logger
from stream_fusion.services.postgresql.schemas import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyInDB,
)

class APIKeyDAO:
    """Class for accessing API key table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.expiration_limit = 15  # Default expiration limit in days

    async def create_key(self, api_key_create: APIKeyCreate) -> APIKeyInDB:
        try:
            api_key = str(uuid.uuid4())
            expiration_date = (
                None
                if api_key_create.never_expire
                else datetime.now(timezone.utc) + timedelta(days=self.expiration_limit)
            )

            new_key = APIKeyModel(
                api_key=api_key,
                is_active=True,
                never_expire=api_key_create.never_expire,
                expiration_date=expiration_date,
                name=api_key_create.name,
            )

            self.session.add(new_key)
            await self.session.commit()
            await self.session.refresh(new_key)

            logger.success(f"Created new API key: {api_key}")
            return APIKeyInDB.model_validate(new_key)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating API key: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_all_keys(self, limit: int, offset: int) -> List[APIKeyInDB]:
        try:
            query = select(APIKeyModel).limit(limit).offset(offset)
            result = await self.session.execute(query)
            keys = [APIKeyInDB.model_validate(key) for key in result.scalars().all()]
            logger.info(f"Retrieved {len(keys)} API keys")
            return keys
        except Exception as e:
            logger.error(f"Error retrieving API keys: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_key_by_uuid(self, api_key: uuid.UUID) -> Optional[APIKeyInDB]:
        try:
            query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
            result = await self.session.execute(query)
            db_key = result.scalar_one_or_none()
            if db_key:
                logger.info(f"Retrieved API key: {api_key}")
                return APIKeyInDB.model_validate(db_key)
            else:
                logger.warning(f"API key not found: {api_key}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving API key {api_key}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_keys_by_name(self, name: str) -> List[APIKeyInDB]:
        try:
            query = select(APIKeyModel).where(APIKeyModel.name == name)
            result = await self.session.execute(query)
            keys = [APIKeyInDB.model_validate(key) for key in result.scalars().all()]
            logger.info(f"Retrieved {len(keys)} API keys with name: {name}")
            return keys
        except Exception as e:
            logger.error(f"Error retrieving API keys by name {name}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def update_key(
        self, api_key: uuid.UUID, update_data: APIKeyUpdate
    ) -> APIKeyInDB:
        try:
            query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
            result = await self.session.execute(query)
            db_key = result.scalar_one_or_none()

            if not db_key:
                logger.warning(f"API key not found for update: {api_key}")
                raise HTTPException(status_code=404, detail="API key not found")

            if update_data.is_active is not None:
                db_key.is_active = update_data.is_active

            if not db_key.never_expire and update_data.expiration_date:
                db_key.expiration_date = update_data.expiration_date

            await self.session.commit()
            await self.session.refresh(db_key)

            logger.info(f"Updated API key: {api_key}")
            return APIKeyInDB.model_validate(db_key)
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating API key {api_key}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete_key(self, api_key: uuid.UUID) -> bool:
        try:
            query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
            result = await self.session.execute(query)
            db_key = result.scalar_one_or_none()

            if db_key:
                await self.session.delete(db_key)
                await self.session.commit()
                logger.info(f"Deleted API key: {api_key}")
                return True
            else:
                logger.warning(f"API key not found for deletion: {api_key}")
                return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting API key {api_key}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def check_key(self, api_key: uuid.UUID) -> bool:
        try:
            query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
            result = await self.session.execute(query)
            db_key = result.scalar_one_or_none()

            if not db_key or not db_key.is_active:
                logger.warning(f"Invalid or inactive API key: {api_key}")
                return False

            if not db_key.never_expire and db_key.expiration_date < datetime.now(
                timezone.utc
            ):
                logger.warning(f"Expired API key: {api_key}")
                return False

            db_key.total_queries += 1
            db_key.latest_query_date = datetime.now(timezone.utc)
            await self.session.commit()

            logger.debug(f"Valid API key used: {api_key}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error checking API key {api_key}: {str(e)}")
            return False

    async def renew_key(self, api_key: uuid.UUID) -> APIKeyInDB:
        try:
            query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
            result = await self.session.execute(query)
            db_key = result.scalar_one_or_none()

            if not db_key:
                logger.warning(f"API key not found for renewal: {api_key}")
                raise HTTPException(status_code=404, detail="API key not found")

            current_time = datetime.now(timezone.utc)

            if db_key.never_expire:
                logger.warning(f"Attempted to renew non-expiring key: {api_key}")
                raise HTTPException(
                    status_code=400,
                    detail="This key never expires and doesn't need renewal",
                )

            if db_key.expiration_date and db_key.expiration_date > current_time:
                logger.warning(f"Attempted to renew non-expired key: {api_key}")
                raise HTTPException(
                    status_code=400, detail="This key hasn't expired yet"
                )

            db_key.expiration_date = current_time + timedelta(
                days=self.expiration_limit
            )
            db_key.is_active = True

            await self.session.commit()
            await self.session.refresh(db_key)

            logger.success(f"Renewed API key: {api_key}")
            return APIKeyInDB.model_validate(db_key)
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error renewing API key {api_key}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_usage_stats(self) -> List[APIKeyInDB]:
        try:
            query = select(APIKeyModel).order_by(APIKeyModel.latest_query_date.desc())
            result = await self.session.execute(query)
            keys = [APIKeyInDB.model_validate(key) for key in result.scalars().all()]
            logger.info(f"Retrieved usage stats for {len(keys)} API keys")
            return keys
        except Exception as e:
            logger.error(f"Error retrieving usage stats: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def list_active_keys(self) -> List[APIKeyInDB]:
        try:
            query = select(APIKeyModel).where(APIKeyModel.is_active == True)
            result = await self.session.execute(query)
            keys = [APIKeyInDB.model_validate(key) for key in result.scalars().all()]
            logger.info(f"Retrieved {len(keys)} active API keys")
            return keys
        except Exception as e:
            logger.error(f"Error listing active keys: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def update_key_name(self, api_key: uuid.UUID, new_name: str) -> APIKeyInDB:
        try:
            query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
            result = await self.session.execute(query)
            db_key = result.scalar_one_or_none()

            if not db_key:
                logger.warning(f"API key not found for name update: {api_key}")
                raise HTTPException(status_code=404, detail="API key not found")

            db_key.name = new_name
            await self.session.commit()
            await self.session.refresh(db_key)

            logger.info(f"Updated name for API key: {api_key}")
            return APIKeyInDB.model_validate(db_key)
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating name for API key {api_key}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
