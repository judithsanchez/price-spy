from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_db
from app.storage.repositories import StoreRepository, TrackedItemRepository
from app.models.schemas import Store, StoreCreate, StoreUpdate, StoreResponse

router = APIRouter(prefix="/api/stores", tags=["Stores"])


@router.get("", response_model=List[StoreResponse])
async def get_stores(db=Depends(get_db)):
    """Get all stores."""
    try:
        repo = StoreRepository(db)
        return repo.get_all()
    finally:
        db.close()


@router.post("", response_model=StoreResponse, status_code=201)
async def create_store(store: StoreCreate, db=Depends(get_db)):
    """Create a new store."""
    try:
        repo = StoreRepository(db)
        store_name = repo.normalize_name(store.name)

        # Check if already exists
        existing = repo.get_by_name(store_name)
        if existing:
            return existing

        store_id = repo.insert(Store(name=store_name))
        return repo.get_by_id(store_id)
    finally:
        db.close()


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(store_id: int, store_update: StoreCreate, db=Depends(get_db)):
    """Update a store."""
    try:
        repo = StoreRepository(db)
        existing = repo.get_by_id(store_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Store not found")

        store_name = repo.normalize_name(store_update.name)
        repo.update(store_id, Store(name=store_name))
        return repo.get_by_id(store_id)
    finally:
        db.close()


@router.patch("/{store_id}", response_model=StoreResponse)
async def patch_store(store_id: int, store_patch: StoreUpdate, db=Depends(get_db)):
    """Partially update a store."""
    try:
        repo = StoreRepository(db)
        existing = repo.get_by_id(store_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Store not found")

        update_data = store_patch.model_dump(exclude_unset=True)
        if not update_data:
            return existing

        current_data = existing.model_dump()
        for key, value in update_data.items():
            current_data[key] = value

        if "name" in update_data:
            current_data["name"] = repo.normalize_name(current_data["name"])

        repo.update(store_id, Store(**current_data))
        return repo.get_by_id(store_id)
    finally:
        db.close()


@router.delete("/{store_id}")
async def delete_store(store_id: int, db=Depends(get_db)):
    """Delete a store. Blocked if used in tracked items."""
    try:
        repo = StoreRepository(db)
        store = repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        # Check usage in TrackedItems
        tracked_item_repo = TrackedItemRepository(db)
        count = tracked_item_repo.count_by_store(store_id)

        if count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete store '{store.name}'. It is used by {count} tracked items. Update or delete them first.",
            )

        repo.delete(store_id)
        return {"status": "success", "message": "Store deleted"}
    finally:
        db.close()
