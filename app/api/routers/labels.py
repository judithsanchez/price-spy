from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_db
from app.models.schemas import Label, LabelCreate, LabelResponse, LabelUpdate
from app.storage.repositories import LabelRepository

router = APIRouter(prefix="/api/labels", tags=["Labels"])


@router.get("", response_model=list[LabelResponse])
async def get_labels(db=Depends(get_db)):
    """Get all labels."""
    try:
        repo = LabelRepository(db)
        return repo.get_all()
    finally:
        db.close()


@router.get("/search", response_model=list[LabelResponse])
async def search_labels(q: str, db=Depends(get_db)):
    """Search labels by name."""
    try:
        repo = LabelRepository(db)
        return repo.search(q)
    finally:
        db.close()


@router.post("", response_model=LabelResponse, status_code=201)
async def create_label(label: LabelCreate, db=Depends(get_db)):
    """Create a new label."""
    try:
        repo = LabelRepository(db)
        # Check if already exists
        existing = repo.get_by_name(label.name)
        if existing:
            return existing

        label_obj = Label(name=label.name)
        label_id = repo.insert(label_obj)
        return repo.get_by_id(label_id)
    finally:
        db.close()


@router.put("/{label_id}", response_model=LabelResponse)
async def update_label(label_id: int, label_update: LabelCreate, db=Depends(get_db)):
    """Update a label name."""
    try:
        repo = LabelRepository(db)
        existing = repo.get_by_id(label_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Label not found")

        repo.update(label_id, label_update.name)
        return repo.get_by_id(label_id)
    finally:
        db.close()


@router.patch("/{label_id}", response_model=LabelResponse)
async def patch_label(label_id: int, label_patch: LabelUpdate, db=Depends(get_db)):
    """Partially update a label."""
    try:
        repo = LabelRepository(db)
        existing = repo.get_by_id(label_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Label not found")

        if label_patch.name:
            repo.update(label_id, label_patch.name)

        return repo.get_by_id(label_id)
    finally:
        db.close()


@router.delete("/{label_id}")
async def delete_label(label_id: int, db=Depends(get_db)):
    """Delete a label. Automatically removed from tracked items via CASCADE."""
    try:
        repo = LabelRepository(db)
        existing = repo.get_by_id(label_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Label not found")

        repo.delete(label_id)
        return {"status": "success", "message": f"Label '{existing.name}' deleted"}
    finally:
        db.close()
