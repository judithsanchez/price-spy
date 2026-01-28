from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_db
from app.models.schemas import (
    TrackedItem,
    TrackedItemCreate,
    TrackedItemResponse,
    TrackedItemUpdate,
)
from app.storage.repositories import (
    CategoryRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)

router = APIRouter(prefix="/api/tracked-items", tags=["Tracked Items"])


@router.get("", response_model=list[TrackedItemResponse])
async def get_items(db=Depends(get_db)):
    """Get all tracked items with their labels."""
    try:
        repo = TrackedItemRepository(db)
        items = repo.get_all()
        result = []
        for item in items:
            # Map TrackedItem to TrackedItemResponse manually or using helper
            item_dict = item.model_dump()
            item_dict["labels"] = repo.get_labels(int(item.id or 0))
            result.append(TrackedItemResponse(**item_dict))
        return result
    finally:
        db.close()


@router.get("/{item_id}", response_model=TrackedItemResponse)
async def get_item(item_id: int, db=Depends(get_db)):
    """Get a single tracked item by ID with its labels."""
    try:
        repo = TrackedItemRepository(db)
        item = repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Tracked item not found")

        item_dict = item.model_dump()
        item_dict["labels"] = repo.get_labels(int(item.id or 0))
        return TrackedItemResponse(**item_dict)
    finally:
        db.close()


@router.post("", response_model=TrackedItemResponse, status_code=201)
async def create_item(item_in: TrackedItemCreate, db=Depends(get_db)):
    """Create a new tracked item and associate labels."""
    try:
        # Validate product and store exist
        prod_repo = ProductRepository(db)
        product = prod_repo.get_by_id(item_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Size sensitivity validation
        cat_repo = CategoryRepository(db)
        if product.category:
            category = cat_repo.get_by_name(product.category)
            is_size_sensitive = category.is_size_sensitive if category else False

            if is_size_sensitive:
                if not item_in.target_size:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Product category '{product.category}' is size-sensitive. "
                            "'target_size' is required."
                        ),
                    )
            elif item_in.target_size:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product category '{product.category}' is NOT size-sensitive. "
                        "'target_size' must be empty."
                    ),
                )

        store_repo = StoreRepository(db)
        if not store_repo.get_by_id(item_in.store_id):
            raise HTTPException(status_code=404, detail="Store not found")

        repo = TrackedItemRepository(db)
        # Check if URL already tracked (optional, but good for data integrity)
        existing = repo.get_by_url(item_in.url)
        if existing:
            # If it exists, return it with labels
            item_dict = existing.model_dump()
            item_dict["labels"] = repo.get_labels(int(existing.id or 0))
            return TrackedItemResponse(**item_dict)

        item_obj = TrackedItem(
            product_id=item_in.product_id,
            store_id=item_in.store_id,
            url=item_in.url,
            target_size=item_in.target_size,
            quantity_size=item_in.quantity_size,
            quantity_unit=item_in.quantity_unit,
            items_per_lot=item_in.items_per_lot,
        )

        item_id = repo.insert(item_obj)

        # Associate labels if provided
        if item_in.label_ids:
            repo.set_labels(item_id, item_in.label_ids)

        created = repo.get_by_id(item_id)
        if not created:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve created item"
            )
        item_dict = created.model_dump()
        item_dict["labels"] = repo.get_labels(int(item_id))
        return TrackedItemResponse(**item_dict)
    finally:
        db.close()


@router.put("/{item_id}", response_model=TrackedItemResponse)
async def update_item(
    item_id: int,
    item_in: TrackedItemCreate,
    db=Depends(get_db),
):
    """Update a tracked item and replace its labels."""
    try:
        repo = TrackedItemRepository(db)
        existing = repo.get_by_id(item_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tracked item not found")

        # Validate product and size sensitivity
        prod_repo = ProductRepository(db)
        product = prod_repo.get_by_id(item_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        cat_repo = CategoryRepository(db)
        if product.category:
            category = cat_repo.get_by_name(product.category)
            is_size_sensitive = category.is_size_sensitive if category else False

            if is_size_sensitive:
                if not item_in.target_size:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Product category '{product.category}' is size-sensitive. "
                            f"'target_size' is required."
                        ),
                    )
            elif item_in.target_size:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product category '{product.category}' is NOT size-sensitive. "
                        f"'target_size' must be empty."
                    ),
                )

        item_obj = TrackedItem(
            product_id=item_in.product_id,
            store_id=item_in.store_id,
            url=item_in.url,
            target_size=item_in.target_size,
            quantity_size=item_in.quantity_size,
            quantity_unit=item_in.quantity_unit,
            items_per_lot=item_in.items_per_lot,
        )

        repo.update(item_id, item_obj)

        # Replace labels
        if item_in.label_ids is not None:
            repo.set_labels(item_id, item_in.label_ids)

        updated = repo.get_by_id(item_id)
        if not updated:
            raise HTTPException(
                status_code=404, detail="Tracked item not found after operation"
            )
        item_dict = updated.model_dump()
        item_dict["labels"] = repo.get_labels(int(item_id))
        return TrackedItemResponse(**item_dict)
    finally:
        db.close()


@router.patch("/{item_id}", response_model=TrackedItemResponse)
async def patch_item(item_id: int, item_patch: TrackedItemUpdate, db=Depends(get_db)):
    """Partially update a tracked item and its labels."""
    try:
        repo = TrackedItemRepository(db)
        existing = repo.get_by_id(item_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tracked item not found")

        update_data = item_patch.model_dump(exclude_unset=True)
        # Pop label_ids as it's handled separately
        label_ids = update_data.pop("label_ids", None)

        if update_data:
            current_data = existing.model_dump()
            for key, value in update_data.items():
                current_data[key] = value

            repo.update(item_id, TrackedItem(**current_data))

        if label_ids is not None:
            repo.set_labels(item_id, label_ids)

        updated = repo.get_by_id(item_id)
        if not updated:
            raise HTTPException(
                status_code=404, detail="Tracked item not found after operation"
            )
        item_dict = updated.model_dump()
        item_dict["labels"] = repo.get_labels(item_id)
        return TrackedItemResponse(**item_dict)
    finally:
        db.close()


@router.delete("/{item_id}")
async def delete_item(item_id: int, db=Depends(get_db)):
    """
    Delete a tracked item. Labels remain but association is removed via
    labels CASCADE or repository cleanup.
    """
    try:
        repo = TrackedItemRepository(db)
        if not repo.get_by_id(item_id):
            raise HTTPException(status_code=404, detail="Tracked item not found")

        repo.delete(item_id)
        return {"status": "success", "message": "Tracked item deleted"}
    finally:
        db.close()
