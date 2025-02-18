from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models.filter_area import FilterArea
from api.models.property import Property

from database import get_db
from ..models.area import Area

from ..schemas import AreaCreate, AreaUpdate, AreaResponse
from sqlalchemy.orm import Session,joinedload

router = APIRouter()


@router.post("/filter_area/", response_model=None)
def create_filter_area(area_name: str, db: Session = Depends(get_db)):
    try:
        # Create new filter area instance
        db_filter_area = FilterArea(area_name=area_name)
        
        # Add to the session and commit the transaction
        db.add(db_filter_area)
        db.commit()
        
        # Refresh the object to get the auto-generated fields (e.g., ID)
        db.refresh(db_filter_area)
        
        # Return the created filter area
        return db_filter_area
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while adding the area.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while adding the area.")
    
@router.get("/filter_area/", response_model=None)
def get_all_filter_areas(db: Session = Depends(get_db)):
    try:
        return db.query(FilterArea).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching areas.")

# Update a filter area
@router.put("/filter_area/{filter_area_id}", response_model=None)
def update_filter_area(filter_area_id: int, area_name: str, db: Session = Depends(get_db)):
    try:
        db_filter_area = db.query(FilterArea).filter(FilterArea.filter_area_id == filter_area_id).first()
        if not db_filter_area:
            raise HTTPException(status_code=404, detail="Filter area not found.")

        db_filter_area.area_name = area_name
        db_filter_area.edit_date = datetime.utcnow()

        db.commit()
        db.refresh(db_filter_area)
        return db_filter_area
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating the area.")

# Delete a filter area
@router.delete("/filter_area/{filter_area_id}")
def delete_filter_area(filter_area_id: int, db: Session = Depends(get_db)):
    try:
        db_filter_area = db.query(FilterArea).filter(FilterArea.filter_area_id == filter_area_id).first()
        if not db_filter_area:
            raise HTTPException(status_code=404, detail="Filter area not found.")

        db.delete(db_filter_area)
        db.commit()
        return {"message": "Filter area deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the area.")
    
# @router.get("/properties_between_areas/")
# async def get_properties_between_areas(
#     from_area: str = None, to_area: str = None, db: Session = Depends(get_db)
# ):
#     """
#     Retrieve properties between two area names (inclusive of both areas), 
#     with hierarchical data such as city, sublocation, and area details.
#     If no areas are provided, returns all data.
#     """
#     try:
#         # Prepare the result
#         city_list = []

#         # Query to get the area_id for the 'from_area' and 'to_area'
#         if from_area and to_area:
#             start_area = db.query(Area).filter(Area.area_name == from_area).first()
#             end_area = db.query(Area).filter(Area.area_name == to_area).first()

#             if not start_area or not end_area:
#                 raise HTTPException(status_code=404, detail="One or both areas not found.")
            
#             # Fetch only relevant cities, sublocations, and areas based on the given range
#             for city in db.query(City).all():
#                 sublocation_list = []

#                 sublocations = db.query(Sublocation).filter(Sublocation.city_id == city.city_id).all()
#                 for sublocation in sublocations:
#                     area_list = []
#                     areas = db.query(Area).filter(Area.sublocation_id == sublocation.sublocation_id).all()

#                     for area in areas:
#                         # Filter areas that are between start_area and end_area
#                         if area.filter_area_id < start_area.filter_area_id or area.filter_area_id > end_area.filter_area_id:
#                             continue  # Skip areas outside the specified range
                        
#                         # Fetch properties in the current area
#                         property_list = []
#                         properties_in_area = db.query(Property).filter(
#                             Property.area_id == area.filter_area_id
#                         ).options(
#                             joinedload(Property.descriptions),
#                             joinedload(Property.lease_sales),
#                             joinedload(Property.property_types),
#                         ).all()

#                         for property_obj in properties_in_area:
#                             property_detail_list = []
#                             property_details = db.query(PropertyDetails).filter(
#                                 PropertyDetails.property_code == property_obj.property_code
#                             ).all()

#                             for detail in property_details:
#                                 property_detail_list.append({
#                                     "floor": detail.floor,
#                                     "unit_no": detail.unit_no,
#                                     "wing": detail.wing,
#                                     "car_parking": detail.car_parking,
#                                     "rate_buy": detail.rate_buy,
#                                     "rate_lease": detail.rate_lease,
#                                     "remarks": detail.remarks,
#                                     "builtup": detail.builtup,
#                                     "carpet": detail.carpet,
#                                     "contacts": [
#                                         {"contact_person": contact.contact_person,
#                                          "email": contact.email,
#                                          "mobile": contact.mobile,
#                                          "contact_person_address": contact.contact_person_address}
#                                         for contact in detail.contacts
#                                     ]
#                                 })

#                             property_list.append({
#                                 "property_code": property_obj.property_code,
#                                 "project_name": property_obj.project_name,
#                                 "building": property_obj.building,
#                                 "address2": property_obj.address2,
#                                 "description": property_obj.descriptions.description,
#                                 "area": area.area_name,
#                                 "pin": property_obj.pin,
#                                 "company": property_obj.company,
#                                 "status_code": property_obj.status_code,
#                                 "property_type": property_obj.property_types.category,
#                                 "c_status": property_obj.c_status,
#                                 "lease_type": property_obj.lease_sales.lease_type,
#                                 "usp": property_obj.usp,
#                                 "property_details": property_detail_list
#                             })

#                         if property_list:
#                             area_list.append({
#                                 "area_name": area.area_name,
#                                 "properties": property_list
#                             })

#                     if area_list:
#                         sublocation_list.append({
#                             "sublocation_name": sublocation.sublocation_name,
#                             "areas": area_list
#                         })

#                 if sublocation_list:
#                     city_list.append({
#                         "city_name": city.city_name,
#                         "sublocations": sublocation_list
#                     })

#         else:
#             # If no 'from_area' and 'to_area' are provided, return all data
#             for city in db.query(City).all():
#                 sublocation_list = []

#                 sublocations = db.query(Sublocation).filter(Sublocation.city_id == city.city_id).all()
#                 for sublocation in sublocations:
#                     area_list = []
#                     areas = db.query(Area).filter(Area.sublocation_id == sublocation.sublocation_id).all()

#                     for area in areas:
#                         # Fetch properties in the current area
#                         property_list = []
#                         properties_in_area = db.query(Property).filter(
#                             Property.area_id == area.area_id
#                         ).options(
#                             joinedload(Property.descriptions),
#                             joinedload(Property.lease_sales),
#                             joinedload(Property.property_types),
#                         ).all()

#                         for property_obj in properties_in_area:
#                             property_detail_list = []
#                             property_details = db.query(PropertyDetails).filter(
#                                 PropertyDetails.property_code == property_obj.property_code
#                             ).all()

#                             for detail in property_details:
#                                 property_detail_list.append({
#                                     "floor": detail.floor,
#                                     "unit_no": detail.unit_no,
#                                     "wing": detail.wing,
#                                     "car_parking": detail.car_parking,
#                                     "rate_buy": detail.rate_buy,
#                                     "rate_lease": detail.rate_lease,
#                                     "remarks": detail.remarks,
#                                     "builtup": detail.builtup,
#                                     "carpet": detail.carpet,
#                                     "contacts": [
#                                         {"contact_person": contact.contact_person,
#                                          "email": contact.email,
#                                          "mobile": contact.mobile,
#                                          "contact_person_address": contact.contact_person_address}
#                                         for contact in detail.contacts
#                                     ]
#                                 })

#                             property_list.append({
#                                 "property_code": property_obj.property_code,
#                                 "project_name": property_obj.project_name,
#                                 "building": property_obj.building,
#                                 "address2": property_obj.address2,
#                                 "description": property_obj.descriptions.description,
#                                 "area": area.area_name,
#                                 "pin": property_obj.pin,
#                                 "company": property_obj.company,
#                                 "status_code": property_obj.status_code,
#                                 "property_type": property_obj.property_types.category,
#                                 "c_status": property_obj.c_status,
#                                 "lease_type": property_obj.lease_sales.lease_type,
#                                 "usp": property_obj.usp,
#                                 "property_details": property_detail_list
#                             })

#                         if property_list:
#                             area_list.append({
#                                 "area_name": area.area_name,
#                                 "properties": property_list
#                             })

#                     if area_list:
#                         sublocation_list.append({
#                             "sublocation_name": sublocation.sublocation_name,
#                             "areas": area_list
#                         })

#                 if sublocation_list:
#                     city_list.append({
#                         "city_name": city.city_name,
#                         "sublocations": sublocation_list
#                     })

#         return city_list

#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail=f"A database error occurred while fetching property hierarchy data.{e}")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
