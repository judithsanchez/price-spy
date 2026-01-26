from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_db
from app.storage.repositories import CategoryRepository, ProductRepository
from app.models.schemas import Category, CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"]
)

@router.get("", response_model=List[CategoryResponse])
async def get_categories(db=Depends(get_db)):
    """Get all categories."""
    try:
        repo = CategoryRepository(db)
        categories = repo.get_all()
        return categories
    finally:
        db.close()

@router.get("/search", response_model=List[CategoryResponse])
async def search_categories(q: str, db=Depends(get_db)):
    """Search categories by name."""
    try:
        repo = CategoryRepository(db)
        categories = repo.search(q)
        return categories
    finally:
        db.close()

@router.post("", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db=Depends(get_db)):
    """Create a new category with mandatory initial capitalization."""
    try:
        repo = CategoryRepository(db)
        category_name = repo.normalize_name(category.name)
        
        # Check if already exists
        existing = repo.get_by_name(category_name)
        if existing:
            return existing
            
        new_cat = Category(name=category_name, is_size_sensitive=category.is_size_sensitive)
        repo.insert(new_cat)
        result = repo.get_by_name(category_name)
        return result
    finally:
        db.close()

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category: CategoryCreate, db=Depends(get_db)):
    """Update a category with mandatory initial capitalization."""
    try:
        repo = CategoryRepository(db)
        old_category = repo.get_by_id(category_id)
        if not old_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category_name = repo.normalize_name(category.name)
        
        # Update products if name changed
        if category_name != old_category.name:
            db.execute(
                "UPDATE products SET category = ? WHERE category = ?",
                (category_name, old_category.name)
            )
        
        # Update category
        updated = Category(name=category_name, is_size_sensitive=category.is_size_sensitive)
        repo.update(category_id, updated)
        
        result = repo.get_by_id(category_id)
        return result
    finally:
        db.close()

@router.patch("/{category_id}", response_model=CategoryResponse)
async def patch_category(category_id: int, category_update: CategoryUpdate, db=Depends(get_db)):
    """Partially update a category with super granular control."""
    try:
        repo = CategoryRepository(db)
        existing = repo.get_by_id(category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Category not found")

        update_data = category_update.model_dump(exclude_unset=True)
        if not update_data:
            return existing

        # Handle capitalization for name update
        if "name" in update_data:
            update_data["name"] = repo.normalize_name(update_data["name"])
            # Update product links if name changes
            if update_data["name"] != existing.name:
                db.execute(
                    "UPDATE products SET category = ? WHERE category = ?",
                    (update_data["name"], existing.name)
                )

        # Merge and create updated object
        current_data = existing.model_dump()
        for key, value in update_data.items():
            current_data[key] = value
        
        updated_category = Category(**current_data)
        repo.update(category_id, updated_category)
        
        return repo.get_by_id(category_id)
    finally:
        db.close()

@router.delete("/{category_id}")
async def delete_category(category_id: int, db=Depends(get_db)):
    """Delete a category. Blocked if assigned to any products."""
    try:
        repo = CategoryRepository(db)
        category = repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
            
        # Check if used by products
        prod_repo = ProductRepository(db)
        products = prod_repo.get_by_category(category.name)
        if products:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete category '{category.name}'. It is assigned to {len(products)} products. Please update those products first."
            )
        
        repo.delete(category_id)
        return {"status": "success", "message": "Category deleted"}
    finally:
        db.close()
