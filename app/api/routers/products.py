from typing import Literal, cast

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_db
from app.models.schemas import (
    Category,
    Product,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.storage.repositories import (
    CategoryRepository,
    ProductRepository,
    TrackedItemRepository,
)


class MergeRequest(BaseModel):
    """Request schema for merging two items, specifying the source and target IDs."""

    source_id: int
    target_id: int


router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
async def get_products(db=Depends(get_db)):
    """Get all products."""
    try:
        repo = ProductRepository(db)
        products = repo.get_all()
        return products
    finally:
        db.close()


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db=Depends(get_db)):
    """Create a new product."""
    try:
        repo = ProductRepository(db)

        # Build kwargs, excluding None values to use schema defaults
        kwargs = {
            "name": product.name,
            "category": product.category,
            "purchase_type": product.purchase_type,
            "target_price": product.target_price,
            "target_unit": product.target_unit,
            "planned_date": product.planned_date,
        }

        # Auto-create category if it doesn't exist
        cat_repo = CategoryRepository(db)
        category_name = cat_repo.normalize_name(product.category)

        if not cat_repo.get_by_name(category_name):
            cat_repo.insert(Category(name=category_name))

        # Override with normalized version
        kwargs["category"] = category_name

        new_product = Product(
            name=str(kwargs["name"]),
            category=str(kwargs["category"]),
            purchase_type=cast(
                Literal["recurring", "one_time"], kwargs["purchase_type"]
            ),
            target_price=float(kwargs["target_price"])
            if kwargs["target_price"]
            else None,
            target_unit=str(kwargs["target_unit"]) if kwargs["target_unit"] else None,
            planned_date=str(kwargs["planned_date"])
            if kwargs["planned_date"]
            else None,
        )
        product_id = repo.insert(new_product)
        created = repo.get_by_id(product_id)
        return created
    finally:
        db.close()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db=Depends(get_db)):
    """Get a product by ID."""
    try:
        repo = ProductRepository(db)
        product = repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        db.close()


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate, db=Depends(get_db)):
    """Update a product."""
    try:
        repo = ProductRepository(db)
        existing = repo.get_by_id(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        # Build updated product object
        updated_product = Product(
            name=product.name,
            category=product.category,
            purchase_type=product.purchase_type,
            target_price=product.target_price,
            target_unit=product.target_unit,
            planned_date=product.planned_date,
        )

        # Auto-create category if it doesn't exist
        if product.category:
            cat_repo = CategoryRepository(db)
            if not cat_repo.get_by_name(product.category):
                cat_repo.insert(Category(name=product.category))

        repo.update(product_id, updated_product)
        result = repo.get_by_id(product_id)
        return result
    finally:
        db.close()


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db=Depends(get_db)):
    """Delete a product."""
    try:
        repo = ProductRepository(db)
        existing = repo.get_by_id(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        # Cascade delete tracked items
        ti_repo = TrackedItemRepository(db)
        ti_repo.delete_by_product(product_id)

        repo.delete(product_id)
    finally:
        db.close()


@router.get("/search", response_model=list[ProductResponse])
async def search_products(q: str, db=Depends(get_db)):
    """Search products by name."""
    try:
        repo = ProductRepository(db)
        return repo.search(q)
    finally:
        db.close()


@router.get("/summary")
async def get_products_summary(db=Depends(get_db)):
    """Get aggregated stats for products."""
    try:
        repo = ProductRepository(db)
        all_products = repo.get_all()
        orphans = repo.find_orphans()

        return {
            "total_products": len(all_products),
            "orphaned_products": len(orphans),
            "active_categories": len({p.category for p in all_products if p.category}),
        }
    finally:
        db.close()


@router.patch("/{product_id}", response_model=ProductResponse)
async def patch_product(
    product_id: int, product_update: ProductUpdate, db=Depends(get_db)
):
    """Partially update a product with super granular control."""
    try:
        repo = ProductRepository(db)
        existing = repo.get_by_id(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get only the fields provided in the request
        update_data = product_update.model_dump(exclude_unset=True)
        if not update_data:
            return existing

        if update_data.get("category"):
            cat_repo = CategoryRepository(db)
            category_name = cat_repo.normalize_name(update_data["category"])
            update_data["category"] = category_name
            if not cat_repo.get_by_name(category_name):
                cat_repo.insert(Category(name=category_name))

        # Merge with existing data
        current_data = existing.model_dump()
        for key, value in update_data.items():
            current_data[key] = value

        updated_product = Product(
            name=str(current_data["name"]),
            category=str(current_data["category"]),
            purchase_type=cast(
                Literal["recurring", "one_time"], current_data["purchase_type"]
            ),
            target_price=float(current_data["target_price"])
            if current_data["target_price"]
            else None,
            target_unit=str(current_data["target_unit"])
            if current_data["target_unit"]
            else None,
            planned_date=str(current_data["planned_date"])
            if current_data["planned_date"]
            else None,
        )

        repo.update(product_id, updated_product)
        return repo.get_by_id(product_id)
    finally:
        db.close()


@router.post("/merge")
async def merge_products(request: MergeRequest, db=Depends(get_db)):
    """Merge two products."""
    try:
        repo = ProductRepository(db)
        if not repo.get_by_id(request.source_id) or not repo.get_by_id(
            request.target_id
        ):
            raise HTTPException(
                status_code=404, detail="One or both products not found"
            )

        repo.merge(request.source_id, request.target_id)
        return {
            "status": "success",
            "message": f"Product {request.source_id} merged into {request.target_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/bulk-delete")
async def bulk_delete_products(product_ids: list[int], db=Depends(get_db)):
    """Delete multiple products at once."""
    try:
        repo = ProductRepository(db)
        repo.bulk_delete(product_ids)
        return {"status": "success", "message": f"{len(product_ids)} products deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
