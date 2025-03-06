from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from api.models.description import Description
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
        property_type_db = db.query(Description).filter(
            Description.des_id == furnished_property.des_code
        ).first()
        
        if not property_type_db:
            raise HTTPException(status_code=400, detail="Description type does not exist.")
        
        furnished_property_obj = FurnishedProperty(
            #property_code=furnished_property.property_code,
            des_code=furnished_property.des_code,
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
        raise HTTPException(status_code=500, detail=f"A database error occurred while creating furnished property data.{e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.{e}")
    

@router.get("/furnished_properties/")
def get_furnished_properties(db: Session = Depends(get_db)):
    try:
        all_data = []
        properties = db.query(FurnishedProperty) \
            .options(joinedload(FurnishedProperty.description), joinedload(FurnishedProperty.property)) \
            .all()

        for r in properties:
            data = {
                "id": r.id,
                #"property_code": r.property_code,
                "conference_rooms": r.conference_rooms,
                "des_code": r.des_code,
                "description": r.description.description if r.description else None,
                "cafeteria_seats": r.cafeteria_seats,
                "workstations": r.workstations,
                "washrooms": r.washrooms,
                "workstation_type_cubicle": r.workstation_type_cubicle,
                "pantry_area": r.pantry_area,
                "workstation_type_linear": r.workstation_type_linear,
                "backup_ups_room": r.backup_ups_room,
                "workstation_type_both": r.workstation_type_both,
                "server_electrical_room": r.server_electrical_room,
                "cabins": r.cabins,
                "reception_waiting_area": r.reception_waiting_area,
                "meeting_rooms": r.meeting_rooms,
                "edit_date": r.edit_date,
            }
            all_data.append(data)

        return all_data

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching furnished property data.")

    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
@router.get("/furnished_properties/{Furnished_d}")
def get_furnished_property(Furnished_d: int, db: Session = Depends(get_db)):
    try:
        property_obj = (
            db.query(FurnishedProperty)
            .options(joinedload(FurnishedProperty.description), joinedload(FurnishedProperty.property))
            .filter(FurnishedProperty.id == Furnished_d)
            .first()
        )

        if not property_obj:
            raise HTTPException(status_code=404, detail="Furnished property not found.")

        data = {
            "id": property_obj.id,
            #"property_code": property_obj.property_code,
            "conference_rooms": property_obj.conference_rooms,
            #"des_code": property_obj.des_code,
            "description": property_obj.description.description if property_obj.description else None,
            "cafeteria_seats": property_obj.cafeteria_seats,
            "workstations": property_obj.workstations,
            "washrooms": property_obj.washrooms,
            "workstation_type_cubicle": property_obj.workstation_type_cubicle,
            "pantry_area": property_obj.pantry_area,
            "workstation_type_linear": property_obj.workstation_type_linear,
            "backup_ups_room": property_obj.backup_ups_room,
            "workstation_type_both": property_obj.workstation_type_both,
            "server_electrical_room": property_obj.server_electrical_room,
            "cabins": property_obj.cabins,
            "reception_waiting_area": property_obj.reception_waiting_area,
            "meeting_rooms": property_obj.meeting_rooms,
            "edit_date": property_obj.edit_date,
        }

        return data

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching furnished property data.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.{e}")

@router.put("/furnished_properties/{Furnished_d}")
def update_furnished_property(
    Furnished_d: int,
    furnished_property: FurnishedPropertyUpdate,  
    db: Session = Depends(get_db)
):
    try:
        existing_property = db.query(FurnishedProperty).filter(FurnishedProperty.id == Furnished_d).first()
        
        if not existing_property:
            raise HTTPException(status_code=404, detail="Furnished property not found.")

        if furnished_property.des_code:
            existing_property.des_code = furnished_property.des_code
        if furnished_property.workstations is not None:
            existing_property.workstations = furnished_property.workstations
        if furnished_property.workstation_type_cubicle is not None:
            existing_property.workstation_type_cubicle = furnished_property.workstation_type_cubicle
        if furnished_property.workstation_type_linear is not None:
            existing_property.workstation_type_linear = furnished_property.workstation_type_linear
        if furnished_property.workstation_type_both is not None:
            existing_property.workstation_type_both = furnished_property.workstation_type_both
        if furnished_property.cabins is not None:
            existing_property.cabins = furnished_property.cabins
        if furnished_property.meeting_rooms is not None:
            existing_property.meeting_rooms = furnished_property.meeting_rooms
        if furnished_property.conference_rooms is not None:
            existing_property.conference_rooms = furnished_property.conference_rooms
        if furnished_property.cafeteria_seats is not None:
            existing_property.cafeteria_seats = furnished_property.cafeteria_seats
        if furnished_property.washrooms is not None:
            existing_property.washrooms = furnished_property.washrooms
        if furnished_property.pantry_area is not None:
            existing_property.pantry_area = furnished_property.pantry_area
        if furnished_property.backup_ups_room is not None:
            existing_property.backup_ups_room = furnished_property.backup_ups_room
        if furnished_property.server_electrical_room is not None:
            existing_property.server_electrical_room = furnished_property.server_electrical_room
        if furnished_property.reception_waiting_area is not None:
            existing_property.reception_waiting_area = furnished_property.reception_waiting_area

        db.commit()
        return {"message": "Furnished property updated successfully", "id": existing_property.id}
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"A database error occurred while updating furnished property data.{e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. {e}")


@router.delete("/furnished_properties/{property_id}")
def delete_furnished_property(property_id: int, db: Session = Depends(get_db)):
    try:
        property_obj = db.query(FurnishedProperty).filter(FurnishedProperty.id == property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Furnished property not found.")
        
        db.delete(property_obj)
        db.commit()
        return {"message": "Furnished property deleted successfully"}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"A database error occurred while delete furnished property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.")
