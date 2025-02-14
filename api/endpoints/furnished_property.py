from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from ..models.furnished_property import FurnishedProperty
from ..models.propertyTypes  import PropertyTypes
from ..schemas import FurnishedPropertyCreate, FurnishedPropertyUpdate
from datetime import datetime

router = APIRouter()

@router.post("/furnished_properties/")
def create_furnished_property(
    furnished_property: FurnishedPropertyCreate, 
    db: Session = Depends(get_db)
):
    try:
        property_type_db = db.query(PropertyTypes).filter(
            PropertyTypes.type_id == furnished_property.property_type_id
        ).first()
        
        if not property_type_db:
            raise HTTPException(status_code=400, detail="Property type does not exist.")
        
        furnished_property_obj = FurnishedProperty(
            property_type_id=furnished_property.property_type_id,
            workstations=furnished_property.workstations,
            workstation_type_cubicle=furnished_property.workstation_type_cubicle,
            workstation_type_linear=furnished_property.workstation_type_linear,
            workstation_type_both=furnished_property.workstation_type_both,
            cabins=furnished_property.cabins,
            meeting_rooms=furnished_property.meeting_rooms,
            conference_rooms=furnished_property.conference_rooms,
            cafeteria_seats=furnished_property.cafeteria_seats,
            washrooms=furnished_property.washrooms,
            pantry_area=furnished_property.pantry_area,
            backup_ups_room=furnished_property.backup_ups_room,
            server_electrical_room=furnished_property.server_electrical_room,
            reception_waiting_area=furnished_property.reception_waiting_area,
        )
        
        db.add(furnished_property_obj)
        db.commit()

        return {"message": "Furnished property created successfully", "id": furnished_property_obj.id}
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"A database error occurred while creating furnished property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.")
    
# Get All Furnished Properties
@router.get("/furnished_properties/")
def get_furnished_properties(db: Session = Depends(get_db)):
    properties = db.query(FurnishedProperty).all()
    return properties

# Get Furnished Property by ID
@router.get("/furnished_properties/{property_id}")
def get_furnished_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = db.query(FurnishedProperty).filter(FurnishedProperty.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Furnished property not found.")
    return property_obj

# Update Furnished Property
@router.put("/furnished_properties/{property_id}")
def update_furnished_property(
    property_id: int,
    furnished_property: FurnishedPropertyUpdate,
    db: Session = Depends(get_db)
):
    property_obj = db.query(FurnishedProperty).filter(FurnishedProperty.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Furnished property not found.")
    
    for field, value in furnished_property.dict(exclude_unset=True).items():
        setattr(property_obj, field, value)
    
    db.commit()
    db.refresh(property_obj)
    return {"message": "Furnished property updated successfully", "id": property_obj.id}

# Delete Furnished Property
@router.delete("/furnished_properties/{property_id}")
def delete_furnished_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = db.query(FurnishedProperty).filter(FurnishedProperty.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Furnished property not found.")
    
    db.delete(property_obj)
    db.commit()
    return {"message": "Furnished property deleted successfully"}
