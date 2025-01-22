from datetime import datetime
from fastapi import FastAPI, APIRouter, HTTPException, Depends, dependencies
from pydantic import BaseModel
import pytz
from api.models.property import Property
from ..models.propertyDetails import PropertyDetails
from database import get_db
from sqlalchemy.orm import Session
from ..models.user import AriyanspropertiesUser
from auth.auth_bearer import JWTBearer, get_admin, get_current_user
from ..schemas import PropertyDetailsCreate,PropertyDetailsUpdate
from ..models.user import AriyanspropertiesUser
from sqlalchemy.exc import SQLAlchemyError


router= APIRouter()


@router.post("/add_property_details/", response_model=None) #dependencies=[Depends(JWTBearer()), Depends(get_admin)]
def create_property_detail(property_detail: PropertyDetailsCreate, db: Session = Depends(get_db), current_user:AriyanspropertiesUser=Depends(get_current_user)):
    utc_now = pytz.utc.localize(datetime.utcnow())
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    try:
        db_property_detail =PropertyDetails(
            property_code =property_detail.property_code,
            rate_buy =property_detail.rate_buy,
            rate_lease =property_detail.rate_lease,
            floor =property_detail.floor,
            unit_no =property_detail.unit_no, 
            wing =property_detail.wing,
            car_parking =property_detail.car_parking, 
            remarks =property_detail.remarks,
            edit_date =ist_now, 
            user_id =current_user.user_id
            )
        db.add(db_property_detail)
        db.commit()
        db.refresh(db_property_detail)
        return db_property_detail
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while adding property detail.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while adding property detail.")

@router.get("/get_all_property_details/", response_model=None)
def get_all_property_details(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)):
    try:
        property_details = db.query(PropertyDetails).filter(PropertyDetails.user_id == current_user.user_id).all()
        return property_details
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching property details.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching property details.")


@router.get("/property_details/{property_detail_id}", response_model=None)
def get_property_detail_by_id(
    property_detail_id: int,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property_detail = db.query(PropertyDetails).filter(PropertyDetails.id == property_detail_id,PropertyDetails.user_id == current_user.user_id).first()
        if not property_detail:
            raise HTTPException(status_code=404, detail="Property detail not found.")
        return property_detail
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching property detail.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching property detail")
    
@router.put("/property_details/{property_detail_id}", response_model=None)
def update_property_detail(
    property_detail_id: int,
    property_detail: PropertyDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        db_property_detail = db.query(PropertyDetails).filter(PropertyDetails.id == property_detail_id,).first()

        if not db_property_detail:
            raise HTTPException(status_code=404, detail="Property detail not found.")
        
        if property_detail.property_code:
            property_code_exists = db.query(Property).filter(Property.property_code == property_detail.property_code).first()
            if not property_code_exists:
                raise HTTPException(status_code=400, detail="Property code does not exist in the property table.")

        if property_detail.property_code is not None:
            db_property_detail.property_code = property_detail.property_code
        if property_detail.rate_buy is not None:
            db_property_detail.rate_buy = property_detail.rate_buy
        if property_detail.rate_lease is not None:
            db_property_detail.rate_lease = property_detail.rate_lease
        if property_detail.floor is not None:
            db_property_detail.floor = property_detail.floor
        if property_detail.unit_no is not None:
            db_property_detail.unit_no = property_detail.unit_no
        if property_detail.wing is not None:
            db_property_detail.wing = property_detail.wing
        if property_detail.car_parking is not None:
            db_property_detail.car_parking = property_detail.car_parking
        if property_detail.remarks is not None:
            db_property_detail.remarks = property_detail.remarks

        db.commit()
        db.refresh(db_property_detail)

        return {"message": "property detail updated successfully.","property_detail":db_property_detail}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating property detail.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurredwhile updating property detail.")

    

@router.delete("/property_details/{property_detail_id}", response_model=None)
def delete_property_detail(
    property_detail_id: int,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        db_property_detail = db.query(PropertyDetails).filter(PropertyDetails.id == property_detail_id,PropertyDetails.user_id == current_user.user_id).first()
        if not db_property_detail:
            raise HTTPException(status_code=404, detail="Property detail not found.")
        
        db.delete(db_property_detail)
        db.commit()
        return {"message": "Property detail deleted successfully.","property_detail_id":property_detail_id}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting property detail.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while deleting property detail.")




