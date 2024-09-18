from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from stream_fusion.services.postgresql.dependencies import get_db_session
from stream_fusion.services.postgresql.models.apikey_model import APIKeyModel
from stream_fusion.services.postgresql.schemas import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyInDB,
)
import uuid
from datetime import datetime, timedelta


class APIKeyDAO:
    """Class for accessing API key table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.expiration_limit = 15  # Default expiration limit in days

    async def create_key(self, api_key_create: APIKeyCreate) -> APIKeyInDB:
        api_key = str(uuid.uuid4())
        expiration_date = (
            None
            if api_key_create.never_expire
            else datetime.utcnow() + timedelta(days=self.expiration_limit)
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

        return APIKeyInDB.model_validate(new_key)

    async def get_all_keys(self, limit: int, offset: int) -> List[APIKeyInDB]:
        query = select(APIKeyModel).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [APIKeyInDB.model_validate(key) for key in result.scalars().all()]

    async def get_key_by_uuid(self, api_key: uuid.UUID) -> Optional[APIKeyInDB]:
        query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()
        return APIKeyInDB.model_validate(db_key) if db_key else None

    async def get_keys_by_name(self, name: str) -> List[APIKeyInDB]:
        """
        Get API key models by name.
        :param name: name of API key instances.
        :return: List of API key models.
        """
        query = select(APIKeyModel).where(APIKeyModel.name == name)
        result = await self.session.execute(query)
        return [APIKeyInDB.model_validate(key) for key in result.scalars().all()]

    async def update_key(
        self, api_key: uuid.UUID, update_data: APIKeyUpdate
    ) -> APIKeyInDB:
        """
        Update an existing API key.
        :param api_key: UUID of the API key to update.
        :param update_data: APIKeyUpdate model with update details.
        :return: Updated API key model.
        """
        query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()

        if not db_key:
            raise HTTPException(status_code=404, detail="API key not found")

        if update_data.is_active is not None:
            db_key.is_active = update_data.is_active

        if not db_key.never_expire and update_data.expiration_date:
            db_key.expiration_date = update_data.expiration_date

        await self.session.commit()
        await self.session.refresh(db_key)

        return APIKeyInDB.model_validate(db_key)

    async def delete_key(self, api_key: uuid.UUID) -> bool:
        """
        Delete an API key.
        :param api_key: UUID of the API key to delete.
        :return: True if deleted, False if not found.
        """
        query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()

        if db_key:
            await self.session.delete(db_key)
            await self.session.commit()
            return True
        return False

    async def check_key(self, api_key: uuid.UUID) -> bool:
        """
        Check if an API key is valid and increment its usage.
        :param api_key: UUID of the API key to check.
        :return: True if valid, False otherwise.
        """
        query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()

        if not db_key or not db_key.is_active:
            return False

        if not db_key.never_expire and db_key.expiration_date < datetime.utcnow():
            return False

        db_key.total_queries += 1
        db_key.latest_query_date = datetime.utcnow()
        await self.session.commit()

        return True

    async def get_usage_stats(self) -> List[APIKeyInDB]:
        query = select(APIKeyModel).order_by(APIKeyModel.latest_query_date.desc())
        result = await self.session.execute(query)
        return [APIKeyInDB.model_validate(key) for key in result.scalars().all()]

    async def list_active_keys(self) -> List[APIKeyInDB]:
        query = select(APIKeyModel).where(APIKeyModel.is_active == True)
        result = await self.session.execute(query)
        return [APIKeyInDB.model_validate(key) for key in result.scalars().all()]

    async def update_key_name(self, api_key: uuid.UUID, new_name: str) -> APIKeyInDB:
        query = select(APIKeyModel).where(APIKeyModel.api_key == str(api_key))
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()

        if not db_key:
            raise HTTPException(status_code=404, detail="API key not found")

        db_key.name = new_name
        await self.session.commit()
        await self.session.refresh(db_key)

        return APIKeyInDB.model_validate(db_key)
