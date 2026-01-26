from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_db
from app.storage.repositories import UnitRepository, ProductRepository, TrackedItemRepository
from app.models.schemas import Unit, UnitCreate, UnitUpdate, UnitResponse

router = APIRouter(
    prefix="/api/units",
    tags=["Units"]
)

@router.get("", response_model=List[UnitResponse])
async def get_units(db=Depends(get_db)):
    """Get all measurement units."""
    try:
        repo = UnitRepository(db)
        return repo.get_all()
    finally:
        db.close()

@router.post("", response_model=UnitResponse, status_code=201)
async def create_unit(unit: UnitCreate, db=Depends(get_db)):
    """Create a new unit."""
    try:
        repo = UnitRepository(db)
        existing = repo.get_by_name(unit.name)
        if existing:
            return existing
        
        unit_id = repo.insert(Unit(name=unit.name))
        return repo.get_by_id(unit_id)
    finally:
        db.close()

@router.put("/{unit_id}", response_model=UnitResponse)
async def update_unit(unit_id: int, unit_update: UnitCreate, db=Depends(get_db)):
    """Update a unit and cascade changes to products and items."""
    try:
        repo = UnitRepository(db)
        existing = repo.get_by_id(unit_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        repo.update(unit_id, Unit(name=unit_update.name))
        return repo.get_by_id(unit_id)
    finally:
        db.close()

@router.patch("/{unit_id}", response_model=UnitResponse)
async def patch_unit(unit_id: int, unit_patch: UnitUpdate, db=Depends(get_db)):
    """Partially update a unit."""
    try:
        repo = UnitRepository(db)
        existing = repo.get_by_id(unit_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        update_data = unit_patch.model_dump(exclude_unset=True)
        if not update_data:
            return existing
            
        current_data = existing.model_dump()
        for key, value in update_data.items():
            current_data[key] = value
            
        repo.update(unit_id, Unit(**current_data))
        return repo.get_by_id(unit_id)
    finally:
        db.close()

@router.delete("/{unit_id}")
async def delete_unit(unit_id: int, db=Depends(get_db)):
    """Delete a unit. Blocked if used in products or tracked items."""
    try:
        repo = UnitRepository(db)
        unit = repo.get_by_id(unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
            
        # Check usage in Products
        prod_repo = ProductRepository(db)
        # We need a get_by_unit search or similar, or just manual query
        products = db.execute("SELECT id FROM products WHERE target_unit = ?", (unit.name,)).fetchall()
        
        # Check usage in TrackedItems
        tracked_items = db.execute("SELECT id FROM tracked_items WHERE quantity_unit = ?", (unit.name,)).fetchall()
        
        if products or tracked_items:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete unit '{unit.name}'. It is used by {len(products)} products and {len(tracked_items)} tracked items. Update them first."
            )
        
        repo.delete(unit_id)
        return {"status": "success", "message": "Unit deleted"}
    finally:
        db.close()
