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

@router.post("/property/", response_model=None)
def create_property(
    property: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property_code = generate_property_code(db=db)

        existing_property = db.query(Property).filter(Property.property_code == property_code).first()
        if existing_property:
            raise HTTPException(status_code=400, detail="Property code already exists.")
        
        property_type_db = db.query(PropertyTypes).join(Property).filter(Property.property_type == property.property_type).first()
        if not property_type_db:
            raise HTTPException(status_code=400, detail="Property type does not exist.")
        
        property_lease_code_exists = db.query(LeaseSale).filter(LeaseSale.lease_id == property.lease_code).first()
        if not property_lease_code_exists:
            raise HTTPException(status_code=400, detail="Lease code does not exist.")
        
        property_des_code_exists = db.query(Description).filter(Description.des_id == property.des_code).first()
        if not property_des_code_exists:
            raise HTTPException(status_code=400, detail="Description code does not exist.")

        property_obj = Property(
            property_code=property_code,
            user_id=current_user.user_id,
            project_name=property.project_name,
            building=property.building,
            address2=property.address2,
            city=property.city,
            area_id=property.area_id,
            pin=property.pin,
            company=property.company,
            status_code=property.status_code,
            property_type=property.property_type,  
            c_status=property.c_status,
            lease_code=property.lease_code,  
            des_code=property.des_code, 
            usp=property.usp,
        )
        db.add(property_obj)
        db.commit()

        # Log the creation action
        log_action=Logs(
            user_id=current_user.user_id,
            action="Property Created",
            property_id=property_obj.property_code,
            timestamp=ist_now,
        )
        db.add(log_action)
        db.commit()

        return {"message": "Property created successfully", "property_code": property_obj.property_code}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while creating property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while creating property data: {str(e)}")


@router.get("/property/{property_code}", response_model=None)
async def get_property_by_code(property_code: str, db: Session = Depends(get_db),current_user: AriyanspropertiesUser = Depends(get_current_user)):
    try:
        # Fetch the property with the given property_code
        property_obj = db.query(Property).options(
            joinedload(Property.lease_sales),  # Eagerly load LeaseSale
            joinedload(Property.descriptions),  # Eagerly load Description
            joinedload(Property.area),  # Eagerly load Area
            joinedload(Property.user)  # Eagerly load User details (name)
        ).filter(Property.property_code == property_code).first()

        # If no property is found, raise HTTP exception
        if not property_obj:
            raise HTTPException(status_code=404, detail=f"Property with property_code {property_code} not found")

        # Return the property details with related names

        log_action = Logs(
                user_id=current_user.user_id,
                action="Property Fetched",
                property_id=property_obj.property_code,
                timestamp=ist_now,
            )
        db.add(log_action)
        db.commit()
        property_data = {
            "property_code": property_obj.property_code,
            "address2": property_obj.address2,
            "des_code": property_obj.des_code,
            "description": property_obj.descriptions.description if property_obj.descriptions else None,
            "user_id": property_obj.user_id,
            "user_name": property_obj.user.user_name if property_obj.user else None,
            "city": property_obj.city,
            "area_id": property_obj.area_id,
            "area_name": property_obj.area.area_name if property_obj.area else None,
            "pin": property_obj.pin,
            "usp": property_obj.usp,
            "company": property_obj.company,
            "edit_date": property_obj.edit_date,
            "status_code": property_obj.status_code,
            "property_type": property_obj.property_type,  # Directly access property_type as it's a column, not a relationship
            "project_name": property_obj.project_name,
            "c_status": property_obj.c_status,
            "building": property_obj.building,
            "lease_code": property_obj.lease_code,
            "lease_lease_type": property_obj.lease_sales.lease_type if property_obj.lease_sales else None
        }

        return property_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/propertyget_all/", response_model=None)
async def get_all_properties(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        # Fetch properties with related data using joinedload
        property_objs = db.query(Property) \
            .options(
                joinedload(Property.lease_sales),  # Eagerly load LeaseSale
                joinedload(Property.descriptions),  # Eagerly load Description
                 joinedload(Property.property_types), 
                joinedload(Property.area),  # Eagerly load Area
                joinedload(Property.user)  # Eagerly load User details (name)
            ).all()

        # If no properties are found, raise HTTP exception
        if not property_objs:
            raise HTTPException(status_code=404, detail="No properties found")

        # Create a list of property data to return
        property_list = []
        for property_obj in property_objs:

            log_action = Logs(
                user_id=current_user.user_id,
                action="Property Fetched",
                property_id=property_obj.property_code,
                timestamp=ist_now,
            )
            db.add(log_action)
            db.commit()

            property_data = {
                "property_code": property_obj.property_code,
                "address2": property_obj.address2,
                "des_code": property_obj.des_code,
                "description": property_obj.descriptions.description,
                "user_id": property_obj.user_id,
                "user_name": property_obj.user.user_name,  # Access the user's name
                "city": property_obj.city,
                "area_id": property_obj.area_id,
                "area_name": property_obj.area.area_name,
                "pin": property_obj.pin,
                "usp": property_obj.usp,
                "company": property_obj.company,
                "edit_date": property_obj.edit_date,
                "status_code": property_obj.status_code,
                "property_type": property_obj.property_type,  # Directly access property_type
                "property_type_category": property_obj.property_types.category,
                "project_name": property_obj.project_name,
                "c_status": property_obj.c_status,
                "building": property_obj.building,
                "lease_code": property_obj.lease_code,
                "lease_lease_type": property_obj.lease_sales.lease_type
            }
            property_list.append(property_data)

        # Return the list of properties with related names
        return property_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    
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

@router.delete("/delete_property_data/{property_code}", response_model=None)
def delete_property(
    property_code: str,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property = db.query(Property).filter(Property.property_code == property_code).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found.")
        
        # Log the creation action
        log_action=Logs(
            user_id=current_user.user_id,
            action="Property Deleted",
            property_id=property_code,
        )
        db.add(log_action)
        db.commit()

        db.delete(property)
        db.commit()
        
        return {"message": "Property deleted successfully.", "property_code":property_code}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while deleting property data.")