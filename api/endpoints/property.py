from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import pytz
from sqlalchemy.orm import Session,joinedload
from api.models.description import Description
from api.models.leaseSale import LeaseSale
from api.models.logs import Logs
from api.models.propertyTypes import PropertyTypes
from api.models.user import AriyanspropertiesUser
from auth.auth_bearer import get_current_user
from ..models.property import Property
from ..schemas import PropertyCreate,PropertyUpdate
from database import get_db
from ..models.property import generate_property_code
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

utc_now = pytz.utc.localize(datetime.utcnow())
ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))



def generate_property_code(db: Session):
    return f"PROP-{int(datetime.utcnow().timestamp())}"

@router.post("/property/", response_model=PropertyCreate)
def create_property(
    property: PropertyCreate,
    db: Session = Depends(get_db),
    current_user :AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property_code = generate_property_code(db=db)

        if db.query(Property).filter(Property.property_code == property_code).first():
            raise HTTPException(status_code=400, detail="Property code already exists.")
        
        if not db.query(PropertyTypes).filter(PropertyTypes.type_id == property.property_type).first():
            raise HTTPException(status_code=400, detail="Property type does not exist.")
        
        if not db.query(LeaseSale).filter(LeaseSale.lease_id == property.lease_code).first():
            raise HTTPException(status_code=400, detail="Lease code does not exist.")
        
        if not db.query(Description).filter(Description.des_id == property.des_code).first():
            raise HTTPException(status_code=400, detail="Description code does not exist.")

        property_obj = Property(
            property_code=property_code,
            user_id=current_user.user_id,
            building_name=property.building_name,
            full_address=property.full_address,
            sublocation=property.sublocation,
            city=property.city,
            des_code=property.des_code,
            LL_outright=property.LL_outright,
            property_type=property.property_type,  
            poss_status=property.poss_status,
            Reopen_date=property.Reopen_date,
            east_west=property.east_west,
        )
        db.add(property_obj)
        db.commit()
        db.refresh(property_obj)

        log_action = Logs(
            user_id=current_user.user_id,
            action="Property Created",
            property_id=property_obj.id,
            timestamp=datetime.utcnow()
        )
        db.add(log_action)
        db.commit()

        return property_obj
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating property.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/property/", response_model=None)
def get_all_properties(db: Session = Depends(get_db)):
    """Fetch all properties from the database."""
    properties = db.query(Property).all()
    return properties

@router.get("/property/{property_code}", response_model=None)
def get_property_by_id(property_code: str, db: Session = Depends(get_db)):
    """Fetch a single property by its ID."""
    property_obj = db.query(Property).filter(Property.property_code == property_code).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj


# @router.put("/update_property_data/{property_code}", response_model=None)
# def update_property(
#     property_code: str,
#     property_update: PropertyUpdate,
#     db: Session = Depends(get_db),
#     current_user: AriyanspropertiesUser = Depends(get_current_user)
# ):
#     try:
#         # Fetch the existing property by code
#         db_property = db.query(Property).filter(Property.property_code == property_code).first()

#         if not db_property:
#             raise HTTPException(status_code=404, detail="Property not found.")

#         # Fetch and update property_type if provided
#         if property_update.property_type:
#             property_type_db = db.query(PropertyTypes).filter(PropertyTypes.type_id == property_update.property_type).first()
#             if not property_type_db:
#                 raise HTTPException(status_code=400, detail="Property type does not exist.")
#             db_property.property_type = property_type_db  # Assign the actual PropertyTypes object

#         # Fetch and update lease_code if provided
#         if property_update.lease_code:
#             property_lease_code_exists = db.query(LeaseSale).filter(LeaseSale.lease_id == property_update.lease_code).first()
#             if not property_lease_code_exists:
#                 raise HTTPException(status_code=400, detail="Lease code does not exist.")
#             db_property.lease_code = property_lease_code_exists  # Assign the actual LeaseSale object

#         # Fetch and update des_code if provided
#         if property_update.des_code:
#             property_des_code_exists = db.query(Description).filter(Description.des_id == property_update.des_code).first()
#             if not property_des_code_exists:
#                 raise HTTPException(status_code=400, detail="Description code does not exist.")
#             db_property.des_code = property_des_code_exists  # Assign the actual Description object

#         # Update other fields only if provided
#         if property_update.building is not None:
#             db_property.building = property_update.building
#         if property_update.address2 is not None:
#             db_property.address2 = property_update.address2
#         if property_update.city is not None:
#             db_property.city = property_update.city
#         if property_update.area is not None:
#             db_property.area = property_update.area
#         if property_update.pin is not None:
#             db_property.pin = property_update.pin
#         if property_update.company is not None:
#             db_property.company = property_update.company
#         if property_update.status_code is not None:
#             db_property.status_code = property_update.status_code
#         if property_update.c_status is not None:
#             db_property.c_status = property_update.c_status
#         if property_update.usp is not None:
#             db_property.usp = property_update.usp

#         # Commit the changes to the database
#         db.commit()
#         db.refresh(db_property)

#         return {"message": "Property data updated successfully.", "property_code": db_property.property_code}

#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as db_exc:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while updating property data.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred while updating property data: {str(e)}")

@router.delete("/property/{property_id}", response_model=dict)
def delete_property(property_code: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Delete a property by its ID."""
    property_obj = db.query(Property).filter(Property.property_code == property_code).first()
    
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    db.delete(property_obj)
    db.commit()

    # Log the deletion action
    log_entry = Logs(
        user_id=current_user["user_id"],
        action="Property Deleted",
        property_id=property_code,
        timestamp=datetime.utcnow(),
    )
    db.add(log_entry)
    db.commit()

    return {"message": "Property deleted successfully", "property_id": property_code}
