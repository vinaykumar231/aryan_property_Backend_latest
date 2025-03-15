from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, APIRouter
import pytz
from sqlalchemy import or_
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
from ..schemas import PropertySchema
import traceback
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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
            raise HTTPException(status_code=403, detail="You do not have permission to add property.")
        
        property_code = generate_property_code(db)

        # reopen_db = Reopen(
        #     availability=property_data.availability,
        #     lease_out=property_data.lease_out,
        #     reopen_date=property_data.reopen_date,
        #     sold_out=property_data.sold_out,
        # )
        # db.add(reopen_db)
        # db.flush()

        des_code_exists = db.query(Description).filter(Description.des_id == property_data.des_code).first()
        
        if not des_code_exists:
            raise HTTPException(status_code=404, detail="Description code not found.")

        property_type_exists = db.query(PropertyTypes).filter(
            PropertyTypes.type_id == property_data.property_type
        ).first()
        if not property_type_exists:
            raise HTTPException(status_code=404,detail="Property type not found.")

        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        property_obj = Property(
            property_code=property_code,
            furnished_property_id=property_data.furnished_property_id,
            user_id=current_user.user_id,
            building_name=property_data.building_name,
            full_address=property_data.full_address,
            sublocation=property_data.sublocation,
            #location=property_data.location,
            city=property_data.city,
            des_code=property_data.des_code,
            LL_outright=property_data.LL_outright,
            property_type=property_data.property_type,
            poss_status=property_data.poss_status,
            Reopen_date=property_data.reopen_date,
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
                raise HTTPException(
                    status_code=404, detail=f"Filter area {area_data.filter_area_id} not found"
                )

            # Ensure unit_floor_wing is not empty before accessing index 0
            

            area = Area(
                property_code=property_obj.property_code,
                filter_area_id=area_data.filter_area_id,
                built_up_area=area_data.built_up_area,
                carpet_up_area=area_data.carpet_up_area,
                efficiency=area_data.efficiency,
                car_parking=area_data.car_parking,
                rental_psf=area_data.rental_psf,
                outright_rate_psf=area_data.outright_rate_psf,
                #floor_wing_unit_id=wing_floor_unit_db.floor_wing_unit_id,
                created_date=ist_now
            )
            db.add(area)
            db.flush()

            if area_data.unit_floor_wing:
                for wing_data in area_data.unit_floor_wing:
                    wing_floor_unit_db = Floor_wing_unit(
                        area_id=area.area_id,
                        wing=wing_data.wing,  
                        floor=wing_data.floor,
                        unit_number=wing_data.unit_number,
                    )
                    db.add(wing_floor_unit_db)
                    db.flush()

            else:
                wing_floor_unit_db = None

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
            action="property data added",
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
        print(e)
        raise HTTPException(status_code=404, detail=f"A database error occurred while add property data.{e}")
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while add property data{e}")
    


@router.get("/get_all_properties/v3")
async def get_all_properties(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        if not current_user.can_view:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view properties."
            )

        # Load relationships properly
        properties = db.query(Property).options(
            joinedload(Property.descriptions),  
            joinedload(Property.property_types),  
            joinedload(Property.contacts),  
            #joinedload(Property.reopen),
            joinedload(Property.area).joinedload(Area.filter_area),  
            joinedload(Property.area).joinedload(Area.floor_wing_unit_number),
            joinedload(Property.furnished_properties),
            joinedload(Property.user)  
        ).all()

        if not properties:
            raise HTTPException(status_code=404, detail="No properties found.")

        property_list = []
        for property_obj in properties:
            
            area_list = [
                {
                    "area_name": area.filter_area.area_name if area.filter_area else None,
                    "built_up_area": area.built_up_area,
                    "carpet_up_area": area.carpet_up_area,
                    "efficiency": area.efficiency,
                    "car_parking": area.car_parking,
                    "rental_psf": area.rental_psf,
                    "outright_rate_psf": area.outright_rate_psf,
                    "floor_wing_unit_number": [
                        {
                            "floor": wing.floor,
                            "wing": wing.wing,
                            "unit_number": wing.unit_number
                        } 
                        for wing in area.floor_wing_unit_number  # Iterate over each floor_wing_unit
                    ]
                }
                for area in property_obj.area
            ]

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

            # Extracting furnished property details
            furnished_property_data = None
            if property_obj.furnished_properties:
                furnished_property_data = {
                    "workstations": property_obj.furnished_properties.workstations,
                    "workstation_type_cubicle": property_obj.furnished_properties.workstation_type_cubicle,
                    "workstation_type_linear": property_obj.furnished_properties.workstation_type_linear,
                    "workstation_type_both": property_obj.furnished_properties.workstation_type_both,
                    "cabins": property_obj.furnished_properties.cabins,
                    "meeting_rooms": property_obj.furnished_properties.meeting_rooms,
                    "conference_rooms": property_obj.furnished_properties.conference_rooms,
                    "cafeteria_seats": property_obj.furnished_properties.cafeteria_seats,
                    "washrooms": property_obj.furnished_properties.washrooms,
                    "pantry_area": property_obj.furnished_properties.pantry_area,
                    "backup_ups_room": property_obj.furnished_properties.backup_ups_room,
                    "server_electrical_room": property_obj.furnished_properties.server_electrical_room,
                    "reception_waiting_area": property_obj.furnished_properties.reception_waiting_area,
                    "edit_date": property_obj.furnished_properties.edit_date
                }

            description_text = property_obj.descriptions.description if property_obj.descriptions else None
            property_text = property_obj.property_types.category if property_obj.property_types else None

            # reopen_data = {
            #     "availability": property_obj.reopen.availability if property_obj.reopen else None,
            #     "lease_out": property_obj.reopen.lease_out if property_obj.reopen else None,
            #     "reopen_date": property_obj.reopen.reopen_date if property_obj.reopen else None,
            #     "sold_out": property_obj.reopen.sold_out if property_obj.reopen else None
            # } if property_obj.reopen else {}
            
            property_list.append({
                "property_code": property_obj.property_code,
                "user_name":property_obj.user.user_name,
                "building_name": property_obj.building_name,
                "full_address": property_obj.full_address,
                "sublocation": property_obj.sublocation,
                #"location": property_obj.location,
                "city": property_obj.city,
                "description": description_text,
                "LL_outright": property_obj.LL_outright,
                "property_type": property_text,
                "poss_status": property_obj.poss_status,
                "east_west": property_obj.east_west,
                "reopen_data": property_obj.Reopen_date,
                "areas": area_list,
                "contacts": contact_list,
                "furnished_details": furnished_property_data
                
            })

        return property_list

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while retrieving property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while retrieving property data.")

    

@router.get("/get_all_properties/")
async def get_all_properties_by_area(
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user),
    from_area: str = None,
    to_area: str = None
):
    try:
        if not current_user.can_view:
            raise HTTPException(status_code=403, detail="You do not have permission to view properties.")

        area_query = db.query(FilterArea)
        area_db = area_query.filter(FilterArea.area_name == from_area).first() if from_area else None
        area_db2 = area_query.filter(FilterArea.area_name == to_area).first() if to_area else None

        query = db.query(Property).join(Area)

        if area_db and area_db2:
            query = query.filter(Area.filter_area_id.between(area_db.filter_area_id, area_db2.filter_area_id))

        properties = query.options(
            joinedload(Property.descriptions),
            joinedload(Property.property_types),
            joinedload(Property.contacts),
            joinedload(Property.area).joinedload(Area.filter_area),
            joinedload(Property.area).joinedload(Area.floor_wing_unit_number),
            joinedload(Property.furnished_properties),
            joinedload(Property.user)
        ).all()

        if not properties:
            raise HTTPException(status_code=404, detail="No properties found.")

        property_list = []
        for property_obj in properties:
            area_list = [
                {
                    "area_name": area.filter_area.area_name if area.filter_area else None,
                    "built_up_area": area.built_up_area,
                    "carpet_up_area": area.carpet_up_area,
                    "efficiency": area.efficiency,
                    "car_parking": area.car_parking,
                    "rental_psf": area.rental_psf,
                    "outright_rate_psf": area.outright_rate_psf,
                    "floor_wing_unit_number": [
                        {
                            "floor": wing.floor,
                            "wing": wing.wing,
                            "unit_number": wing.unit_number
                        } 
                        for wing in area.floor_wing_unit_number
                    ]
                }
                for area in property_obj.area
            ]

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
            # Extracting furnished property details
            furnished_property_data = None
            if property_obj.furnished_properties:
                furnished_property_data = {
                    "workstations": property_obj.furnished_properties.workstations,
                    "workstation_type_cubicle": property_obj.furnished_properties.workstation_type_cubicle,
                    "workstation_type_linear": property_obj.furnished_properties.workstation_type_linear,
                    "workstation_type_both": property_obj.furnished_properties.workstation_type_both,
                    "cabins": property_obj.furnished_properties.cabins,
                    "meeting_rooms": property_obj.furnished_properties.meeting_rooms,
                    "conference_rooms": property_obj.furnished_properties.conference_rooms,
                    "cafeteria_seats": property_obj.furnished_properties.cafeteria_seats,
                    "washrooms": property_obj.furnished_properties.washrooms,
                    "pantry_area": property_obj.furnished_properties.pantry_area,
                    "backup_ups_room": property_obj.furnished_properties.backup_ups_room,
                    "server_electrical_room": property_obj.furnished_properties.server_electrical_room,
                    "reception_waiting_area": property_obj.furnished_properties.reception_waiting_area,
                    "edit_date": property_obj.furnished_properties.edit_date
                }

            description_text = property_obj.descriptions.description if property_obj.descriptions else None
            property_text = property_obj.property_types.category if property_obj.property_types else None

            property_list.append({
                "property_code": property_obj.property_code,
                "user_name":property_obj.user.user_name,
                "building_name": property_obj.building_name,
                "full_address": property_obj.full_address,
                "sublocation": property_obj.sublocation,
                "city": property_obj.city,
                "description": description_text,
                "LL_outright": property_obj.LL_outright,
                "property_type": property_text,
                "poss_status": property_obj.poss_status,
                "east_west": property_obj.east_west,
                "reopen_data": property_obj.Reopen_date,
                "areas": area_list,
                "contacts": contact_list,
                "furnished_details": furnished_property_data
            })

        return property_list

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while retrieving property data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while retrieving property data.")
    
@router.put("/update_property/{property_code}", response_model=None)
async def update_property_with_hierarchy(
    property_code: str,
    property_data: PropertySchema,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        if not current_user.can_edit:
            raise HTTPException(status_code=403, detail="You do not have permission to update property.")
        
        property_obj = db.query(Property).filter(Property.property_code == property_code).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found.")
        
        PropertyTypes_db=db.query(PropertyTypes).filter(PropertyTypes.type_id==property_data.property_type).first()
        if not PropertyTypes_db:
            raise HTTPException(status_code=404, detail="Property type not found")
        
        description_db=db.query(Description).filter(Description.des_id==property_data.des_code).first()
        if not description_db:
            raise HTTPException(status_code=404, detail="Description not found")

        property_obj.furnished_property_id = property_data.furnished_property_id
        property_obj.building_name = property_data.building_name
        property_obj.full_address = property_data.full_address
        property_obj.sublocation = property_data.sublocation
        property_obj.city = property_data.city
        property_obj.des_code = property_data.des_code
        property_obj.LL_outright = property_data.LL_outright
        property_obj.property_type = property_data.property_type
        property_obj.poss_status = property_data.poss_status
        property_obj.Reopen_date = property_data.reopen_date
        property_obj.east_west = property_data.east_west

        db.flush()

        for area_data in property_data.areas:
            area = db.query(Area).filter(Area.property_code == property_code).first()

            db_filter_name=db.query(FilterArea).filter(FilterArea.filter_area_id==area_data.filter_area_id).first()

            if not db_filter_name:
                raise HTTPException(status_code=404, detail="Location not found")
            
            if area:
                area.filter_area_id=db_filter_name.filter_area_id
                area.built_up_area = area_data.built_up_area
                area.carpet_up_area = area_data.carpet_up_area
                area.efficiency = area_data.efficiency
                area.car_parking = area_data.car_parking
                area.rental_psf = area_data.rental_psf
                area.outright_rate_psf = area_data.outright_rate_psf
            else:
                area = Area(
                    property_code=property_code,
                    filter_area_id=area_data.filter_area_id,
                    built_up_area=area_data.built_up_area,
                    carpet_up_area=area_data.carpet_up_area,
                    efficiency=area_data.efficiency,
                    car_parking=area_data.car_parking,
                    rental_psf=area_data.rental_psf,
                    outright_rate_psf=area_data.outright_rate_psf
                )
                db.add(area)
            db.flush()

            db.query(Floor_wing_unit).filter(Floor_wing_unit.area_id == area.area_id).delete()
            for wing_data in area_data.unit_floor_wing:
                wing_floor_unit_db = Floor_wing_unit(
                    area_id=area.area_id,
                    wing=wing_data.wing,
                    floor=wing_data.floor,
                    unit_number=wing_data.unit_number
                )
                db.add(wing_floor_unit_db)
            db.flush()

            db.query(PropertyContacts).filter(PropertyContacts.property_code == property_code).delete()
            for contact_data in area_data.contacts:
                contact = PropertyContacts(
                    property_code=property_code,
                    company_builder_name=contact_data.company_builder_name,
                    address=contact_data.address,
                    conatact_person_1=contact_data.conatact_person_1,
                    conatact_person_2=contact_data.conatact_person_2,
                    conatact_person_number_1=contact_data.conatact_person_number_1,
                    conatact_person_number_2=contact_data.conatact_person_number_2,
                    email=contact_data.email,
                    reffered_by=contact_data.reffered_by
                )
                db.add(contact)
            db.flush()

        db.commit()

        return {"message": "Property with hierarchy updated successfully"}
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"A database error occurred while Updating the property.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while Updating the property.")



@router.delete("/delete_property/{property_code}", response_model=dict)
async def delete_property(
    property_code: str,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property_obj = db.query(Property).options(
            joinedload(Property.descriptions),  
            joinedload(Property.property_types),  
            joinedload(Property.contacts),  
            joinedload(Property.area).joinedload(Area.filter_area),  
            joinedload(Property.area).joinedload(Area.floor_wing_unit_number)
        ).filter(Property.property_code == property_code).first()

        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found.")

        db.query(Logs).filter(Logs.property_id == property_code).delete()

        for area in property_obj.area:
            db.delete(area)

        for contact in property_obj.contacts:
            db.delete(contact)

        if property_obj.property_types:
            db.delete(property_obj.property_types)
        if property_obj.descriptions:
            db.delete(property_obj.descriptions)

        db.delete(property_obj)

        log_action = Logs(
            user_id=current_user.user_id,
            action="property data deleted",
            property_id=property_obj.property_code,
            timestamp=ist_now
        )
        db.add(log_action)
       
        db.commit()

        return {"message": "Property deleted successfully."}
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"A database error occurred while deleting the property: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while deleting the property: {str(e)}")
