from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_db
from app.storage.repositories import PurchaseTypeRepository, ProductRepository
from app.models.schemas import PurchaseType, PurchaseTypeCreate, PurchaseTypeUpdate, PurchaseTypeResponse

router = APIRouter(
    prefix="/api/purchase-types",
    tags=["Purchase Types"]
)

@router.get("", response_model=List[PurchaseTypeResponse])
async def get_purchase_types(db=Depends(get_db)):
    """Get all purchase types (recurring, one_time)."""
    try:
        repo = PurchaseTypeRepository(db)
        return repo.get_all()
    finally:
        db.close()

@router.post("", response_model=PurchaseTypeResponse, status_code=201)
async def create_purchase_type(pt: PurchaseTypeCreate, db=Depends(get_db)):
    """Create a new purchase type."""
    try:
        repo = PurchaseTypeRepository(db)
        existing = repo.get_by_name(pt.name)
        if existing:
            return existing
        
        pt_id = repo.insert(PurchaseType(name=pt.name))
        return repo.get_by_id(pt_id)
    finally:
        db.close()

@router.put("/{pt_id}", response_model=PurchaseTypeResponse)
async def update_purchase_type(pt_id: int, pt_update: PurchaseTypeCreate, db=Depends(get_db)):
    """Update a purchase type and cascade changes to products."""
    try:
        repo = PurchaseTypeRepository(db)
        existing = repo.get_by_id(pt_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Purchase type not found")
        
        repo.update(pt_id, PurchaseType(name=pt_update.name))
        return repo.get_by_id(pt_id)
    finally:
        db.close()

@router.patch("/{pt_id}", response_model=PurchaseTypeResponse)
async def patch_purchase_type(pt_id: int, pt_patch: PurchaseTypeUpdate, db=Depends(get_db)):
    """Partially update a purchase type."""
    try:
        repo = PurchaseTypeRepository(db)
        existing = repo.get_by_id(pt_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Purchase type not found")
        
        update_data = pt_patch.model_dump(exclude_unset=True)
        if not update_data:
            return existing
            
        current_data = existing.model_dump()
        for key, value in update_data.items():
            current_data[key] = value
            
        repo.update(pt_id, PurchaseType(**current_data))
        return repo.get_by_id(pt_id)
    finally:
        db.close()

@router.delete("/{pt_id}")
async def delete_purchase_type(pt_id: int, db=Depends(get_db)):
    """Delete a purchase type. Blocked if used in products."""
    try:
        repo = PurchaseTypeRepository(db)
        pt = repo.get_by_id(pt_id)
        if not pt:
            raise HTTPException(status_code=404, detail="Purchase type not found")
            
        # Check usage in Products
        products = db.execute("SELECT id FROM products WHERE purchase_type = ?", (pt.name,)).fetchall()
        
        if products:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete purchase type '{pt.name}'. It is used by {len(products)} products. Update them first."
            )
        
        repo.delete(pt_id)
        return {"status": "success", "message": "Purchase type deleted"}
    finally:
        db.close()
