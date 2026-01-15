"""API routes for Twitter handle management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import TwitterHandle
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter(prefix="/api/handles", tags=["handles"])

class HandleCreate(BaseModel):
    """Schema for creating a new handle."""
    handle: str
    is_active: bool = True

class HandleUpdate(BaseModel):
    """Schema for updating a handle."""
    handle: str = None
    is_active: bool = None

@router.get("")
async def get_all_handles(db: Session = Depends(get_db)) -> List[Dict]:
    """
    Get all Twitter handles.
    
    Returns:
        List of handle objects
    """
    handles = db.query(TwitterHandle).all()
    return [handle.to_dict() for handle in handles]

@router.post("")
async def create_handle(handle_data: HandleCreate, db: Session = Depends(get_db)) -> Dict:
    """
    Create a new Twitter handle.
    
    Args:
        handle_data: Handle creation data
        
    Returns:
        Created handle object
    """
    # Check if handle already exists
    existing = db.query(TwitterHandle).filter(
        TwitterHandle.handle == handle_data.handle
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Handle already exists")
    
    # Create new handle
    new_handle = TwitterHandle(
        handle=handle_data.handle,
        is_active=handle_data.is_active
    )
    
    db.add(new_handle)
    db.commit()
    db.refresh(new_handle)
    
    return new_handle.to_dict()

@router.put("/{handle_id}")
async def update_handle(
    handle_id: int,
    handle_data: HandleUpdate,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Update a Twitter handle.
    
    Args:
        handle_id: Handle ID to update
        handle_data: Update data
        
    Returns:
        Updated handle object
    """
    handle = db.query(TwitterHandle).filter(TwitterHandle.id == handle_id).first()
    
    if not handle:
        raise HTTPException(status_code=404, detail="Handle not found")
    
    # Update fields
    if handle_data.handle is not None:
        handle.handle = handle_data.handle
    if handle_data.is_active is not None:
        handle.is_active = handle_data.is_active
    
    db.commit()
    db.refresh(handle)
    
    return handle.to_dict()

@router.delete("/{handle_id}")
async def delete_handle(handle_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Delete a Twitter handle.
    
    Args:
        handle_id: Handle ID to delete
        
    Returns:
        Success message
    """
    handle = db.query(TwitterHandle).filter(TwitterHandle.id == handle_id).first()
    
    if not handle:
        raise HTTPException(status_code=404, detail="Handle not found")
    
    db.delete(handle)
    db.commit()
    
    return {"message": "Handle deleted successfully", "id": handle_id}

@router.patch("/{handle_id}/toggle")
async def toggle_handle(handle_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Toggle handle active status.
    
    Args:
        handle_id: Handle ID to toggle
        
    Returns:
        Updated handle object
    """
    handle = db.query(TwitterHandle).filter(TwitterHandle.id == handle_id).first()
    
    if not handle:
        raise HTTPException(status_code=404, detail="Handle not found")
    
    handle.is_active = not handle.is_active
    db.commit()
    db.refresh(handle)
    
    return handle.to_dict()
