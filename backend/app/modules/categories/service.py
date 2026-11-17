from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

from .repository import CategoryRepository


class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = CategoryRepository(db)

    async def list_categories(self) -> list[Category]:
        return await self.repository.list_all()

    async def list_categories_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Category], int]:
        return await self.repository.list_paginated(page=page, page_size=page_size, search=search)

    async def get_category(self, category_id: int) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found.')
        return category

    async def create_category(
        self,
        actor_user_id: int,
        name: str,
        slug: str,
        description: str | None,
        parent_id: int | None,
    ) -> Category:
        normalized_name = name.strip()
        normalized_slug = slug.strip().lower()
        if await self.repository.get_by_name(normalized_name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category name already exists.')
        if await self.repository.get_by_slug(normalized_slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category slug already exists.')
        if parent_id is not None and await self.repository.get_by_id(parent_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent category not found.')

        category = await self.repository.create(
            name=normalized_name,
            slug=normalized_slug,
            description=description,
            parent_id=parent_id,
        )
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='category.create',
            entity_id=category.id,
            details={'name': category.name, 'slug': category.slug},
        )
        await self.db.commit()
        return category

    async def update_category(
        self,
        actor_user_id: int,
        category_id: int,
        name: str | None,
        slug: str | None,
        description: str | None,
        parent_id: int | None,
    ) -> Category:
        category = await self.get_category(category_id)

        if name is not None:
            normalized_name = name.strip()
            existing_name = await self.repository.get_by_name(normalized_name)
            if existing_name and existing_name.id != category.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category name already exists.')
            category.name = normalized_name

        if slug is not None:
            normalized_slug = slug.strip().lower()
            existing_slug = await self.repository.get_by_slug(normalized_slug)
            if existing_slug and existing_slug.id != category.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category slug already exists.')
            category.slug = normalized_slug

        if parent_id == category.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category parent cannot be itself.')

        if parent_id is not None and await self.repository.get_by_id(parent_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent category not found.')

        category.description = description
        category.parent_id = parent_id
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='category.update',
            entity_id=category.id,
            details={'name': category.name, 'slug': category.slug},
        )
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, actor_user_id: int, category_id: int) -> None:
        category = await self.get_category(category_id)
        await self.repository.delete(category)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='category.delete',
            entity_id=category_id,
            details={'name': category.name},
        )
        await self.db.commit()
