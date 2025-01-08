from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import pytz
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from ..models.propertyTypes import PropertyTypes  # Import the PropertyTypes model
from pydantic import BaseModel
from ..schemas import PropertyTypeCreate, PropertyTypeUpdate,PropertyTypeResponse
from database import get_db

router = APIRouter()

@router.post("/property_types/", response_model=None)
def create_property_type(
    property_type: PropertyTypeCreate,
    db: Session = Depends(get_db)
):
    db_property_type = PropertyTypes(type_id=property_type.category[:3].upper() + str(db.query(PropertyTypes).count() + 1), category=property_type.category)
    db.add(db_property_type)
    db.commit()
    db.refresh(db_property_type)
    return db_property_type

@router.get("/property_types/{type_id}", response_model=None)
def get_property_type(
    type_id: str,
    db: Session = Depends(get_db)
):
    db_property_type = db.query(PropertyTypes).filter(PropertyTypes.type_id == type_id).first()
    if not db_property_type:
        raise HTTPException(status_code=404, detail="Property type not found")
    return db_property_type

@router.get("/property_types/")
async def get_property_types(db: Session = Depends(get_db)):
    property_types = db.query(PropertyTypes).all()
    if not property_types:
        raise HTTPException(status_code=404, detail="No property types found")
    return property_types


@router.put("/property_types/{type_id}", response_model=None)
def update_property_type(
    type_id: str,
    property_type_update: PropertyTypeUpdate,
    db: Session = Depends(get_db)
):
    utc_now = pytz.utc.localize(datetime.utcnow())
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    db_property_type = db.query(PropertyTypes).filter(PropertyTypes.type_id == type_id).first()
    if not db_property_type:
        raise HTTPException(status_code=404, detail="Property type not found")
    
    db_property_type.category = property_type_update.category
    db_property_type.edit_date = ist_now
    db.commit()
    db.refresh(db_property_type)
    return db_property_type


@router.delete("/property_types/{type_id}", response_model=None)
def delete_property_type(
    type_id: str,
    db: Session = Depends(get_db)
):
    db_property_type = db.query(PropertyTypes).filter(PropertyTypes.type_id == type_id).first()
    if not db_property_type:
        raise HTTPException(status_code=404, detail="Property type not found")

    db.delete(db_property_type)
    db.commit()
    return db_property_type
