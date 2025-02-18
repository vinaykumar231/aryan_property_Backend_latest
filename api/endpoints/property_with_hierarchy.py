from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, APIRouter
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
from api.models.area import Area
from api.models.description import Description
from api.models.filter_area import FilterArea
from api.models.leaseSale import LeaseSale
from api.models.logs import Logs
from api.models.property import Property, generate_property_code
from api.models.propertyContacts import PropertyContacts
from api.models.propertyTypes import PropertyTypes
from api.models.reopan_date import Reopen
from api.models.user import AriyanspropertiesUser
from api.models.wing_floor_unit import Floor_wing_unit
from auth.auth_bearer import get_current_user
from database import get_db
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging
from ..schemas import CitySchema, CityUpdateSchema
import traceback
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Pydantic Models with corrected field names and validations
class PropertyContactSchema(BaseModel):
    company_builder_name: str
    address: str
    conatact_person_1: Optional[str] = None  # Changed to match DB column name
    conatact_person_2: Optional[str] = None  # Changed to match DB column name
    conatact_person_number_1: Optional[int] = None  # Changed to match DB column name
    conatact_person_number_2: Optional[int] = None  # Changed to match DB column name
    email: str
    reffered_by: Optional[str] = None  # Changed to match DB column name

class AreaSchema(BaseModel):
    filter_area_id: int
    built_up_area: float
    carpet_up_area: float
    efficiency: Optional[float] = None
    car_parking: Optional[str] = None
    rental_psf: Optional[str] = None
    outright_rate_psf: Optional[str] = None
    wing: Optional[str] = None
    floor: Optional[str] = None
    unit_number: Optional[str] = None
    contacts: List[PropertyContactSchema]

class PropertySchema(BaseModel):
    building_name: str
    full_address: str
    sublocation: Optional[str] = None
    location: Optional[str] = None
    city: str
    des_code: str
    LL_outright: str
    property_type: str
    poss_status: Optional[str] = None
    east_west: Optional[str] = None
    availability: Optional[str] = None
    lease_out: Optional[str] = None
    reopen_date: Optional[datetime] = None
    sold_out: Optional[str] = None
    areas: List[AreaSchema]


utc_now = pytz.utc.localize(datetime.utcnow())
ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

@router.post("/add_property_with_hierarchy/", response_model=dict)
async def add_property_with_hierarchy(
    property_data: PropertySchema,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        if not current_user.can_add:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to add property."
            )
        
        property_code = generate_property_code(db)

        reopen_db = Reopen(
            availability=property_data.availability,
            lease_out=property_data.lease_out,
            reopen_date=property_data.reopen_date,
            sold_out=property_data.sold_out,
        )
        db.add(reopen_db)
        db.flush()

        des_code_exists = db.query(Description).filter(
            Description.des_id == property_data.des_code
        ).first()
        if not des_code_exists:
            raise HTTPException(
                status_code=404,
                detail="Description code not found."
            )

        property_type_exists = db.query(PropertyTypes).filter(
            PropertyTypes.type_id == property_data.property_type
        ).first()
        if not property_type_exists:
            raise HTTPException(
                status_code=404,
                detail="Property type not found."
            )

        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        property_obj = Property(
            property_code=property_code,
            user_id=current_user.user_id,
            building_name=property_data.building_name,
            full_address=property_data.full_address,
            sublocation=property_data.sublocation,
            location=property_data.location,
            city=property_data.city,
            des_code=property_data.des_code,
            LL_outright=property_data.LL_outright,
            property_type=property_data.property_type,
            poss_status=property_data.poss_status,
            Reopen_date=reopen_db.id,
            east_west=property_data.east_west,
            created_date=ist_now
        )
        db.add(property_obj)
        db.flush()

        for area_data in property_data.areas:
            filter_area = db.query(FilterArea).filter(
                FilterArea.filter_area_id == area_data.filter_area_id
            ).first()
            if not filter_area:
                raise HTTPException(status_code=404, detail=f"Filter area {area_data.filter_area_id} not found")

            wing_floor_unit_db = Floor_wing_unit(
                wing=area_data.wing,
                floor=area_data.floor,
                unit_number=area_data.unit_number,
            )
            db.add(wing_floor_unit_db)
            db.flush()

            area = Area(
                property_code=property_obj.property_code,
                filter_area_id=area_data.filter_area_id,
                built_up_area=area_data.built_up_area,
                carpet_up_area=area_data.carpet_up_area,
                efficiency=area_data.efficiency,
                car_parking=area_data.car_parking,
                rental_psf=area_data.rental_psf,
                outright_rate_psf=area_data.outright_rate_psf,
                floor_wing_unit_id=wing_floor_unit_db.floor_wing_unit_id,
                created_date=ist_now
            )
            db.add(area)
            db.flush()

            for contact_data in area_data.contacts:
                contact = PropertyContacts(
                    property_code=property_obj.property_code,
                    company_builder_name =contact_data.company_builder_name,
                    address = contact_data.address,
                    conatact_person_1 = contact_data.conatact_person_1,
                    conatact_person_2 = contact_data.conatact_person_2,
                    conatact_person_number_1 = contact_data.conatact_person_number_1,
                    conatact_person_number_2 = contact_data.conatact_person_number_2,
                    email = contact_data.email,
                    reffered_by = contact_data.reffered_by                   
                )
                db.add(contact)
                db.flush()

        log_action = Logs(
            user_id=current_user.user_id,
            action="property added",
            property_id=property_obj.property_code,
            timestamp=ist_now
        )
        db.add(log_action)

        db.commit()

        return {"message": "Property with hierarchy data added successfully"}
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while add property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while add property data")
    


@router.get("/get_all_properties/")
async def get_all_properties(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        # Check if the user has permission to view properties
        if not current_user.can_view:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view properties."
            )
        
        # Query the database to get all properties along with their related data
        properties = db.query(Property).options(
            joinedload(Property.descriptions),  # Join descriptions
            joinedload(Property.property_types),  # Join property types
            joinedload(Property.contacts),  # Join contacts
            joinedload(Property.reopen),
              joinedload(Property.area).joinedload(Area.filter_area),  # Join reopen data
            joinedload(Property.area).joinedload(Area.floor_wing_unit_number)  # Join floor_wing_unit_number
        ).all()

        if not properties:
            raise HTTPException(status_code=404, detail="No properties found.")

        # Prepare the property list
        property_list = []
        for property_obj in properties:
            # Get associated areas and format them
            area_list = [
                {
                    "area_name": area.filter_area.area_name,
                    "built_up_area": area.built_up_area,
                    "carpet_up_area": area.carpet_up_area,
                    "efficiency": area.efficiency,
                    "car_parking": area.car_parking,
                    "rental_psf": area.rental_psf,
                    "outright_rate_psf": area.outright_rate_psf,
                    "floor_wing_unit_number": {
                        "floor": area.floor_wing_unit_number.floor,
                        "wing": area.floor_wing_unit_number.wing,
                        "unit_number": area.floor_wing_unit_number.unit_number
                    }
                }
                for area in property_obj.area
            ]


            # Get associated contacts and format them
            contact_list = [
                {
                    "company_builder_name": contact.company_builder_name,
                    "address": contact.address,
                    "conatact_person_1": contact.conatact_person_1,
                    "conatact_person_2": contact.conatact_person_2,
                    "conatact_person_number_1": contact.conatact_person_number_1,
                    "conatact_person_number_2": contact.conatact_person_number_2,
                    "email": contact.email,
                    "reffered_by": contact.reffered_by
                }
                for contact in property_obj.contacts  
            ]

            description_text = (
                property_obj.descriptions.description if property_obj.descriptions else ""
            )

            property_text = (
                property_obj.property_types.category if property_obj.property_types else ""
            )

            reopen_data = {
                "availability": property_obj.reopen.availability if property_obj.reopen else None,
                "lease_out": property_obj.reopen.lease_out if property_obj.reopen else None,
                "reopen_date": property_obj.reopen.reopen_date if property_obj.reopen else None,
                "sold_out": property_obj.reopen.sold_out if property_obj.reopen else None
            } if property_obj.reopen else {}
            
            

            # Add the formatted property to the list
            property_list.append({
                "building_name": property_obj.building_name,
                "full_address": property_obj.full_address,
                "sublocation": property_obj.sublocation,
                "location": property_obj.location,
                "city": property_obj.city,
                "description": description_text,
                "LL_outright": property_obj.LL_outright,
                "property_type": property_text,
                "poss_status": property_obj.poss_status,
                "east_west": property_obj.east_west,
                "areas": area_list,
                "contacts": contact_list,
                "reopen_data": reopen_data 
            })

        return property_list

    except HTTPException as http_exc:
        # Handle HTTP exceptions (e.g., permission errors)
        raise http_exc
    except SQLAlchemyError as e:
        # Rollback in case of database errors and raise an internal server error
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while retrieving property data.")
    except Exception as e:
        # Handle any other unexpected errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while retrieving property data: {str(e)}")
    

@router.get("/get_all_properties_by_area/")
async def get_all_properties(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user),
    from_area: str = None,  # Optional parameter to filter properties from a specific area
    to_area: str = None  # Optional parameter to filter properties to a specific area
):
    try:
        # Check if the user has permission to view properties
        if not current_user.can_view:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view properties."
            )
        
        # Query to get area ids for the 'from_area' and 'to_area'
        start_area = None
        end_area = None
        if from_area and to_area:
            start_area = db.query(Area).filter(Area.area_name == from_area).first()
            end_area = db.query(Area).filter(Area.area_name == to_area).first()

            if not start_area or not end_area:
                raise HTTPException(status_code=404, detail="One or both areas not found.")
        
        # Query the database to get all properties along with their related data
        properties = db.query(Property).options(
            joinedload(Property.descriptions),  # Join descriptions
            joinedload(Property.property_types),  # Join property types
            joinedload(Property.contacts),  # Join contacts
            joinedload(Property.reopen),
            joinedload(Property.area).joinedload(Area.filter_area),  # Join reopen data
            joinedload(Property.area).joinedload(Area.floor_wing_unit_number)  # Join floor_wing_unit_number
        ).all()

        if not properties:
            raise HTTPException(status_code=404, detail="No properties found.")

        # Prepare the property list
        property_list = []
        for property_obj in properties:
            # Get associated areas and format them
            area_list = []
            for area in property_obj.area:
                # Filter areas between start_area and end_area based on filter_area_id
                if start_area and end_area:
                    if area.filter_area_id < start_area.filter_area_id or area.filter_area_id > end_area.filter_area_id:
                        continue  # Skip areas outside the specified range
                
                # Format area details
                area_list.append({
                    "area_name": area.filter_area.area_name,
                    "built_up_area": area.built_up_area,
                    "carpet_up_area": area.carpet_up_area,
                    "efficiency": area.efficiency,
                    "car_parking": area.car_parking,
                    "rental_psf": area.rental_psf,
                    "outright_rate_psf": area.outright_rate_psf,
                    "floor_wing_unit_number": {
                        "floor": area.floor_wing_unit_number.floor,
                        "wing": area.floor_wing_unit_number.wing,
                        "unit_number": area.floor_wing_unit_number.unit_number
                    }
                })

            # Get associated contacts and format them
            contact_list = [
                {
                    "company_builder_name": contact.company_builder_name,
                    "address": contact.address,
                    "conatact_person_1": contact.conatact_person_1,
                    "conatact_person_2": contact.conatact_person_2,
                    "conatact_person_number_1": contact.conatact_person_number_1,
                    "conatact_person_number_2": contact.conatact_person_number_2,
                    "email": contact.email,
                    "reffered_by": contact.reffered_by
                }
                for contact in property_obj.contacts
            ]

            description_text = (
                property_obj.descriptions.description if property_obj.descriptions else ""
            )

            property_text = (
                property_obj.property_types.category if property_obj.property_types else ""
            )

            reopen_data = {
                "availability": property_obj.reopen.availability if property_obj.reopen else None,
                "lease_out": property_obj.reopen.lease_out if property_obj.reopen else None,
                "reopen_date": property_obj.reopen.reopen_date if property_obj.reopen else None,
                "sold_out": property_obj.reopen.sold_out if property_obj.reopen else None
            } if property_obj.reopen else {}

            # Add the formatted property to the list
            property_list.append({
                "building_name": property_obj.building_name,
                "full_address": property_obj.full_address,
                "sublocation": property_obj.sublocation,
                "location": property_obj.location,
                "city": property_obj.city,
                "description": description_text,
                "LL_outright": property_obj.LL_outright,
                "property_type": property_text,
                "poss_status": property_obj.poss_status,
                "east_west": property_obj.east_west,
                "areas": area_list,
                "contacts": contact_list,
                "reopen_data": reopen_data
            })

        return property_list

    except HTTPException as http_exc:
        # Handle HTTP exceptions (e.g., permission errors)
        raise http_exc
    except SQLAlchemyError as e:
        # Rollback in case of database errors and raise an internal server error
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while retrieving property data.")
    except Exception as e:
        # Handle any other unexpected errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while retrieving property data: {str(e)}")


    
# @router.get("/get_all_property_hierarchy/v2", response_model=None)
# async def get_all_cities(db: Session = Depends(get_db)):
#     try:
#         result = db.execute(select(City))
#         cities = result.scalars().all()

#         city_list = []
#         for city in cities:
#             sublocation_list = []
#             sublocations = db.execute(select(Sublocation).filter(Sublocation.city_id == city.city_id))
#             for sublocation in sublocations.scalars().all():
#                 area_list = []
#                 areas = db.execute(select(Area).filter(Area.sublocation_id == sublocation.sublocation_id))
#                 for area in areas.scalars().all():
#                     property_list = []
#                     properties = db.execute(
#                         select(Property)
#                         .filter(Property.area_id == area.area_id)
#                         .options(
#                             joinedload(Property.descriptions),  
#                             joinedload(Property.lease_sales),
#                             joinedload(Property.property_types),   
#                         )
#                     )

#                     for property_obj in properties.scalars().all():
#                         property_detail_list = []
#                         property_details = db.execute(select(PropertyDetails).filter(PropertyDetails.property_code == property_obj.property_code))
#                         for detail in property_details.scalars().all():
#                             property_detail_list.append({
#                                 "floor": detail.floor,
#                                 "unit_no": detail.unit_no,
#                                 "wing": detail.wing,
#                                 "car_parking": detail.car_parking,
#                                 "rate_buy": detail.rate_buy,
#                                 "rate_lease": detail.rate_lease,
#                                 "remarks": detail.remarks,
#                                 "builtup":detail.builtup,
#                                 "carpet":detail.carpet,
#                                 "contacts": [
#                                     {"contact_person": contact.contact_person, 
#                                      "email": contact.email, 
#                                      "mobile": contact.mobile,
#                                     "contact_person_address": contact.contact_person_address}
#                                     for contact in detail.contacts
#                                 ]
#                             })
                        
#                         property_list.append({
#                             "property_code":property_obj.property_code,
#                             "project_name": property_obj.project_name,
#                             "building": property_obj.building,
#                             "address2": property_obj.address2,
#                             "description": property_obj.descriptions.description,
#                             "area": area.area_name,
#                             "pin": property_obj.pin,
#                             "company": property_obj.company,
#                             "status_code": property_obj.status_code,
#                             "property_type": property_obj.property_types.category,
#                             "c_status": property_obj.c_status,
#                             "lease_type": property_obj.lease_sales.lease_type,
#                             "usp": property_obj.usp,
#                             "property_details": property_detail_list
#                         })
                    
#                     area_list.append({
#                         "area_name": area.area_name,
#                         "properties": property_list
#                     })
                
#                 sublocation_list.append({
#                     "sublocation_name": sublocation.sublocation_name,
#                     "areas": area_list
#                 })
            
#             city_list.append({
#                 "city_name": city.city_name,
#                 "sublocations": sublocation_list
#             })
        
#         # log_action = Logs(
#         #         user_id=current_user.user_id,
#         #         action="Fetched all property hierarchy data",
#         #         property_id=property_obj.property_code,
#         #         timestamp=ist_now,
#         #     )
#         # db.add(log_action)
#         # db.commit()
#         return city_list
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while fetch property hierarchy data.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while fetch property hierarchy data") #f"An unexpected error occurred: {str(e)}"
    

# ### for filter all data based area || from and to ###############################

# @router.get("/get_all_property_hierarchy/", response_model=None)
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


    


# @router.get("/get_property_hierarchy_by_id/{property_id}", response_model=None)
# async def get_property_by_id(property_id: str, db: AsyncSession = Depends(get_db), current_user: AriyanspropertiesUser = Depends(get_current_user)):
#     try:
#         result = db.execute(
#             select(Property)
#             .filter(Property.property_code == property_id)
#             .options(
#                 joinedload(Property.descriptions),
#                 joinedload(Property.lease_sales),
#                 joinedload(Property.area).joinedload(Area.sublocation).joinedload(Sublocation.city)
#             )
#         )
#         property_obj = result.scalars().first()

#         if not property_obj:
#             raise HTTPException(status_code=404, detail="Property not found")

#         details_result = db.execute(
#             select(PropertyDetails).filter(PropertyDetails.property_code == property_id)
#         )
#         property_details = details_result.scalars().all()

#         property_detail_list = []
#         for detail in property_details:
#             property_detail_list.append({
#                 "floor": detail.floor,
#                 "unit_no": detail.unit_no,
#                 "wing": detail.wing,
#                 "car_parking": detail.car_parking,
#                 "rate_buy": detail.rate_buy,
#                 "rate_lease": detail.rate_lease,
#                 "remarks": detail.remarks,
#                 "builtup":detail.builtup,
#                 "carpet":detail.carpet,
                
#             })

#         log_action = Logs(
#                 user_id=current_user.user_id,
#                 action="Fetched all property hierarchy data",
#                 property_id=property_obj.property_code,
#                 timestamp=ist_now,
#             )
#         db.add(log_action)
#         db.commit()

#         return {
#              "city":{
#                 "city_name": property_obj.area.sublocation.city.city_name if property_obj.area and property_obj.area.sublocation else None,
#             },
#             "sublocation":{
#                 "sublocation_name": property_obj.area.sublocation.sublocation_name if property_obj.area else None,
#             },
#             "area":{
#                 "area_name": property_obj.area.area_name if property_obj.area else None,
#             },
#             "properties":{
#                 "project_name": property_obj.project_name,
#                 "building": property_obj.building,
#                 "address2": property_obj.address2,
#                 "description": property_obj.descriptions.description,
#                 "pin": property_obj.pin,
#                 "company": property_obj.company,
#                 "status_code": property_obj.status_code,
#                 "property_type": property_obj.property_type,
#                 "c_status": property_obj.c_status,
#                 "lease_type": property_obj.lease_sales.lease_type,
#                 "usp": property_obj.usp,
#             },
#             "property_details": property_detail_list,
#             "contacts": [
#                     {"contact_person": contact.contact_person, "email": contact.email, "mobile": contact.mobile,  "contact_person_address": contact.contact_person_address}
#                     for contact in detail.contacts
#                 ]
           
#         }
    # except HTTPException as http_exc:
    #     raise http_exc
    # except SQLAlchemyError as e:
    #     db.rollback()
    #     raise HTTPException(status_code=404, detail="A database error occurred while fetch property hierarchy data.")
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred while fetch property hierarchy data") #f"An unexpected error occurred: {str(e)}"


# @router.put("/update_property_details_with_hierarchy/{property_id}", response_model=None)
# async def update_property_hierarchy(
#     property_id: str,
#     property_data: CityUpdateSchema,
#     db: Session = Depends(get_db),
#     current_user: AriyanspropertiesUser = Depends(get_current_user)
# ):
#     try:
#         if not current_user.can_edit:
#             raise HTTPException(status_code=403, detail="You do not have permission to Update property details.")
        
#         property_obj = db.query(Property).filter(Property.property_code == property_id).first()

#         if not property_obj:
#             raise HTTPException(status_code=404, detail="Property not found")

#         if property_data.city_name:
#             city = db.query(City).filter(City.city_name == property_data.city_name).first()
#             if not city:
#                 city = City(city_name=property_data.city_name)
#                 db.add(city)
#                 db.commit()
#             property_obj.city = city.city_name
        
#         for sublocation_data in property_data.sublocations:
#             sublocation = db.query(Sublocation).filter(Sublocation.sublocation_name == sublocation_data.sublocation_name).first()
#             if sublocation:
#                 for area_data in sublocation_data.areas:
#                     area = db.query(Area).filter(Area.area_name == area_data.area_name).first()
#                     if area:
#                         for property_data in area_data.properties:
#                             if property_obj.building == property_data.building:  
#                                 if property_data.building:
#                                     property_obj.building = property_data.building
#                                 if property_data.address2:
#                                     property_obj.address2 = property_data.address2
#                                 if property_data.description:
#                                     description = db.query(Description).filter(Description.des_id == property_obj.des_code).first()
#                                     if description:
#                                         description.description = property_data.description
#                                 if property_data.status_code:
#                                     property_obj.status_code = property_data.status_code
#                                 if property_data.property_type:
#                                     property_obj.property_type = property_data.property_type
                                    
#                                 if property_data.type_id :
#                                     property_obj.property_type  = property_data.type_id 

#                                 if property_data.lease_type:
#                                     lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == property_obj.lease_code).first()
#                                     if lease_sale:
#                                         lease_sale.lease_type = property_data.lease_type
#                                 if property_data.usp:
#                                     property_obj.usp = property_data.usp
#                                 if property_data.project_name: 
#                                     property_obj.project_name = property_data.project_name
                                    
#                                 # Update property details
#                                 for detail_data in property_data.property_details:
#                                     property_detail = db.query(PropertyDetails).filter(PropertyDetails.property_code == property_id).first()
#                                     if property_detail:
#                                         if detail_data.floor:
#                                             property_detail.floor = detail_data.floor
#                                         if detail_data.unit_no:
#                                             property_detail.unit_no = detail_data.unit_no
#                                         if detail_data.wing:
#                                             property_detail.wing = detail_data.wing
#                                         if detail_data.car_parking:
#                                             property_detail.car_parking = detail_data.car_parking
#                                         if detail_data.rate_buy:
#                                             property_detail.rate_buy = detail_data.rate_buy
#                                         if detail_data.rate_lease:
#                                             property_detail.rate_lease = detail_data.rate_lease
#                                         if detail_data.remarks:
#                                             property_detail.remarks = detail_data.remarks
#                                         if detail_data.builtup:
#                                             property_detail.builtup = detail_data.builtup
#                                         if detail_data.carpet:
#                                             property_detail.carpet = detail_data.carpet

#                                         # Update contacts
#                                         for contact_data in detail_data.contacts:
#                                             contact = db.query(PropertyContacts).filter(PropertyContacts.property_detail_id == property_detail.id).first()
#                                             if contact:
#                                                 if contact_data.contact_person:
#                                                     contact.contact_person = contact_data.contact_person
#                                                 if contact_data.email:
#                                                     contact.email = contact_data.email
#                                                 if contact_data.mobile:
#                                                     contact.mobile = contact_data.mobile
#                                                 if contact_data.contact_person_address:  
#                                                     contact.contact_person_address = contact_data.contact_person_address
        
#          # Log the creation action
#         log_action=Logs(
#             user_id=current_user.user_id,
#             action="updated all property hierarchy data ",
#             property_id=property_id,
#         )
#         db.add(log_action)
    
#         db.commit()
#         return {"message": "Property hierarchy updated successfully"}
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"A database error occurred while  updating property hierarchy data.{e}")

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while updating property hierarchy data")




# @router.delete("/delete_property_hierarchy/{property_id}", response_model=None)
# async def delete_property_hierarchy(
#     property_id: str,
#     db: Session = Depends(get_db),
#     current_user: AriyanspropertiesUser = Depends(get_current_user)
# ):
#     try:
#         if not current_user.can_delete:
#             raise HTTPException(status_code=403, detail="You do not have permission to Delete property details.")
        
#         property_details = db.query(PropertyDetails).filter(PropertyDetails.property_code == property_id).first()
#         if not property_details:
#             raise HTTPException(status_code=404, detail="Property not found")
        
#          # Log the creation action
#         log_action=Logs(
#             user_id=current_user.user_id,
#             action="Deleted all property hierarchy data",
#             property_id=property_id,
#         )
#         db.add(log_action)
#         db.commit()

#         db.query(PropertyContacts).filter(PropertyContacts.property_detail_id == property_details.id).delete(synchronize_session=False)

#         db.delete(property_details)

#         property_obj = db.query(Property).filter(Property.property_code == property_id).first()
#         db.delete(property_obj)

#         sublocation_obj = db.query(Sublocation).join(Area).join(Property).filter(Property.property_code == property_id).first()
#         area_obj = db.query(Area).join(Property).filter(Property.property_code == property_id).first()
#         city_obj = db.query(City).join(Sublocation).join(Area).join(Property).filter(Property.property_code == property_id).first()

#         if not db.query(Property).filter(Property.area_id == area_obj.area_id).first():
#             db.delete(area_obj)

#         if not db.query(Area).filter(Area.sublocation_id == sublocation_obj.sublocation_id).first():
#             db.delete(sublocation_obj)

#         if not db.query(Sublocation).filter(Sublocation.city_id == city_obj.city_id).first():
#             db.delete(city_obj)

#         db.commit()

#         return {"message": "Property and associated hierarchy deleted successfully"}

#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while  deleting property hierarchy data.")

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting property hierarchy data")