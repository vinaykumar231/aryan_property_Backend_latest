from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.models.description import Description
from api.models.leaseSale import LeaseSale
from api.models.propertyTypes import PropertyTypes
from api.models.user import AriyanspropertiesUser
from auth.auth_bearer import get_current_user
from ..models.property import Property
from ..schemas import PropertyCreate,PropertyUpdate
from database import get_db
from ..models.property import generate_property_code
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

@router.post("/property/", response_model=None)     #dependencies=[Depends(JWTBearer()), Depends(get_admin)]
def create_property(
    property: PropertyCreate,
    db: Session = Depends(get_db),
    current_user:AriyanspropertiesUser=Depends(get_current_user)
):
    try:
        property_code = generate_property_code(db=db)
        existing_property = db.query(Property).filter(Property.property_code == property_code).first()
        if existing_property:
            raise HTTPException(status_code=400, detail="Property code already exists.")
        
        property_type_db = db.query(Property).filter(PropertyTypes.type_id == property.property_type).first()
        if not property_type_db:
                raise HTTPException(status_code=400, detail="Property type does not exist ")
        
        property_lease_code_exists = db.query(LeaseSale).filter(LeaseSale.lease_id == property.lease_code).first()
        if not property_lease_code_exists:
                raise HTTPException(status_code=400, detail="Lease code does not exist")
        
        property_des_code_exists = db.query(Description).filter(Description.des_id == property.des_code).first()
        if not property_des_code_exists:
                raise HTTPException(status_code=400, detail="Description code does not exist.")

        db_property = Property(
            property_code=property_code,
            user_id=current_user.user_id,
            building=property.building,
            address2=property.address2,
            city=property.city,
            area=property.area,
            pin=property.pin,
            company=property.company,
            status_code=property.status_code,
            property_type=property.property_type,
            c_status=property.c_status,
            lease_code=property.lease_code,
            des_code=property.des_code,
            usp=property.usp
        )

        db.add(db_property)
        db.commit()
        db.refresh(db_property)

        return db_property
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while creating property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating property data.") #f"An unexpected error occurred: {str(e)}"

@router.get("/property/{property_code}", response_model=None)
def get_property(
    property_code: str,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property = db.query(Property).filter(Property.property_code == property_code).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found.")
        return property
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching property data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching property data")


@router.get("/get_all_property_data/", response_model=None)
def get_all_properties(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        properties = db.query(Property).all()
        return properties
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching property data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching property data")
    

@router.put("/update_property_data/{property_code}", response_model=None)
def update_property(
    property_code: str,
    property_update: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        db_property = db.query(Property).filter(Property.property_code == property_code).first()
        if not db_property:
            raise HTTPException(status_code=404, detail="Property not found.")
        
        if property_update.property_type:
            property_type_db = db.query(Property).filter(Property.property_type == property_update.property_type).first()
            if not property_type_db:
                raise HTTPException(status_code=400, detail="Property type does not exist in the property table.")
    
        if property_update.lease_code:
            property_lease_code_exists = db.query(Property).filter(Property.lease_code == property_update.lease_code).first()
            if not property_lease_code_exists:
                raise HTTPException(status_code=400, detail="Lease code does not exist in the property table.")
        
        if property_update.des_code:
            property_des_code_exists = db.query(Property).filter(Property.des_code == property_update.des_code).first()
            if not property_des_code_exists:
                raise HTTPException(status_code=400, detail="Description code does not exist in the property table.")
        
        if property_update.building is not None:
            db_property.building = property_update.building
        if property_update.address2 is not None:
            db_property.address2 = property_update.address2
        if property_update.city is not None:
            db_property.city = property_update.city
        if property_update.area is not None:
            db_property.area = property_update.area
        if property_update.pin is not None:
            db_property.pin = property_update.pin
        if property_update.company is not None:
            db_property.company = property_update.company
        if property_update.status_code is not None:
            db_property.status_code = property_update.status_code
        if property_update.property_type is not None:
            db_property.property_type = property_update.property_type
        if property_update.c_status is not None:
            db_property.c_status = property_update.c_status
        if property_update.lease_code is not None:
            db_property.lease_code = property_update.lease_code
        if property_update.des_code is not None:
            db_property.des_code = property_update.des_code
        if property_update.usp is not None:
            db_property.usp = property_update.usp

        db.commit()
        db.refresh(db_property)

        return {"message": "property data updated successfully.","property":db_property}

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as db_exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while updating property data.")

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

        db.delete(property)
        db.commit()
        return {"message": "Property deleted successfully.", "property":property}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while deleting property data.")