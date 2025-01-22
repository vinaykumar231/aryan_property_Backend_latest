from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, APIRouter
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
from api.models.area import Area
from api.models.city import City
from api.models.description import Description
from api.models.leaseSale import LeaseSale
from api.models.logs import Logs
from api.models.property import Property, generate_property_code
from api.models.propertyContacts import PropertyContacts
from api.models.propertyDetails import PropertyDetails
from api.models.propertyTypes import PropertyTypes
from api.models.sublocation import Sublocation
from api.models.user import AriyanspropertiesUser
from auth.auth_bearer import get_current_user
from database import get_db
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging
from ..schemas import CitySchema, CityUpdateSchema
import traceback

router = APIRouter()

utc_now = pytz.utc.localize(datetime.utcnow())
ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

@router.post("/add_property_details_with_hierarchy/", response_model=None)
async def add_city(
    city_data: CitySchema, 
    db: Session = Depends(get_db), 
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        # Add city
        city = City(city_name=city_data.city_name)
        db.add(city)
        db.flush()

        for sublocation_data in city_data.sublocations:
            sublocation = Sublocation(
                sublocation_name=sublocation_data.sublocation_name,
                city_id=city.city_id,  
            )
            db.add(sublocation)
            db.flush()

            for area_data in sublocation_data.areas:
                area = Area(
                    area_name=area_data.area_name,
                    sublocation_id=sublocation.sublocation_id
                )
                db.add(area)
                db.flush()

                for property_data in area_data.properties:
                    property_code = generate_property_code(db)
                    count = db.query(Description).count() + 1
                    des_id = f"D{count:03}"

                    description = Description(
                        des_id=des_id,
                        description=property_data.description,
                        edit_date=ist_now
                    )
                    db.add(description)
                    db.flush()

                    count = db.query(LeaseSale).count() + 1
                    lease_id = f"L{count:03}"

                    lease_sale = LeaseSale(
                        lease_id=lease_id,
                        lease_type=property_data.lease_type,
                        edit_date=ist_now
                    )
                    db.add(lease_sale)
                    db.flush()

                    property_type = PropertyTypes(
                        type_id=f"{property_data.property_type[:3].upper()}{db.query(PropertyTypes).count() + 1}",
                        category=property_data.property_type,
                        edit_date=ist_now
                    )
                    db.add(property_type)
                    db.flush()

                    property_obj = Property(
                        property_code=property_code,
                        user_id=current_user.user_id,
                        project_name=property_data.project_name,
                        building=property_data.building,
                        address2=property_data.address2,
                        city=city.city_name,
                        area_id=area.area_id,
                        pin=property_data.pin,
                        company=property_data.company,
                        status_code=property_data.status_code,
                        property_type=property_type.type_id,
                        c_status=property_data.c_status,
                        lease_code=lease_sale.lease_id,
                        des_code=description.des_id,
                        usp=property_data.usp,
                    )
                    db.add(property_obj)
                    db.flush()

                    for detail_data in property_data.property_details:
                        property_detail = PropertyDetails(
                            floor=detail_data.floor,
                            unit_no=detail_data.unit_no,
                            wing=detail_data.wing,
                            car_parking=detail_data.car_parking,
                            rate_buy=detail_data.rate_buy,
                            rate_lease=detail_data.rate_lease,
                            remarks=detail_data.remarks,
                            property_code=property_obj.property_code,
                            user_id=current_user.user_id,
                        )
                        db.add(property_detail)
                        db.flush()

                        for contact_data in detail_data.contacts:
                            contact = PropertyContacts(
                                contact_person=contact_data.contact_person,
                                email=contact_data.email,
                                mobile=contact_data.mobile,
                                contact_person_address=contact_data.contact_person_address,
                                property_detail_id=property_detail.id,
                                property_id=property_obj.property_code,
                            )
                            db.add(contact)
        log_action=Logs(
            user_id=current_user.user_id,
            action="Created all property hierarchy data",
            property_id=property_obj.property_code,
            timestamp=ist_now,
        )
        db.add(log_action)
        db.commit()

        db.commit()
        return {"message": "property hierarchy data added successfully"}
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while creating property hierarchy data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating property hierarchy data") #f"An unexpected error occurred: {str(e)}"



@router.get("/get_all_property_hierarchy/", response_model=None)
async def get_all_cities(db: Session = Depends(get_db), current_user: AriyanspropertiesUser = Depends(get_current_user)):
    try:
        result = db.execute(select(City))
        cities = result.scalars().all()

        city_list = []
        for city in cities:
            sublocation_list = []
            sublocations = db.execute(select(Sublocation).filter(Sublocation.city_id == city.city_id))
            for sublocation in sublocations.scalars().all():
                area_list = []
                areas = db.execute(select(Area).filter(Area.sublocation_id == sublocation.sublocation_id))
                for area in areas.scalars().all():
                    property_list = []
                    properties = db.execute(
                        select(Property)
                        .filter(Property.area_id == area.area_id)
                        .options(
                            joinedload(Property.descriptions),  
                            joinedload(Property.lease_sales)   
                        )
                    )

                    for property_obj in properties.scalars().all():
                        property_detail_list = []
                        property_details = db.execute(select(PropertyDetails).filter(PropertyDetails.property_code == property_obj.property_code))
                        for detail in property_details.scalars().all():
                            property_detail_list.append({
                                "floor": detail.floor,
                                "unit_no": detail.unit_no,
                                "wing": detail.wing,
                                "car_parking": detail.car_parking,
                                "rate_buy": detail.rate_buy,
                                "rate_lease": detail.rate_lease,
                                "remarks": detail.remarks,
                                "contacts": [
                                    {"contact_person": contact.contact_person, 
                                     "email": contact.email, 
                                     "mobile": contact.mobile,
                                    "contact_person_address": contact.contact_person_address}
                                    for contact in detail.contacts
                                ]
                            })
                        
                        property_list.append({
                            "project_name": property_obj.project_name,
                            "building": property_obj.building,
                            "address2": property_obj.address2,
                            "description": property_obj.descriptions.description,
                            "area": area.area_name,
                            "pin": property_obj.pin,
                            "company": property_obj.company,
                            "status_code": property_obj.status_code,
                            "property_type": property_obj.property_type,
                            "c_status": property_obj.c_status,
                            "lease_type": property_obj.lease_sales.lease_type,
                            "usp": property_obj.usp,
                            "property_details": property_detail_list
                        })
                    
                    area_list.append({
                        "area_name": area.area_name,
                        "properties": property_list
                    })
                
                sublocation_list.append({
                    "sublocation_name": sublocation.sublocation_name,
                    "areas": area_list
                })
            
            city_list.append({
                "city_name": city.city_name,
                "sublocations": sublocation_list
            })
        
        log_action = Logs(
                user_id=current_user.user_id,
                action="Fetched all property hierarchy data",
                property_id=property_obj.property_code,
                timestamp=ist_now,
            )
        db.add(log_action)
        db.commit()
        return city_list
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while fetch property hierarchy data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetch property hierarchy data") #f"An unexpected error occurred: {str(e)}"

    


@router.get("/get_property_hierarchy_by_id/{property_id}", response_model=None)
async def get_property_by_id(property_id: str, db: AsyncSession = Depends(get_db), current_user: AriyanspropertiesUser = Depends(get_current_user)):
    try:
        result = db.execute(
            select(Property)
            .filter(Property.property_code == property_id)
            .options(
                joinedload(Property.descriptions),
                joinedload(Property.lease_sales),
                joinedload(Property.area).joinedload(Area.sublocation).joinedload(Sublocation.city)
            )
        )
        property_obj = result.scalars().first()

        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        details_result = db.execute(
            select(PropertyDetails).filter(PropertyDetails.property_code == property_id)
        )
        property_details = details_result.scalars().all()

        property_detail_list = []
        for detail in property_details:
            property_detail_list.append({
                "floor": detail.floor,
                "unit_no": detail.unit_no,
                "wing": detail.wing,
                "car_parking": detail.car_parking,
                "rate_buy": detail.rate_buy,
                "rate_lease": detail.rate_lease,
                "remarks": detail.remarks,
                
            })

        log_action = Logs(
                user_id=current_user.user_id,
                action="Fetched all property hierarchy data",
                property_id=property_obj.property_code,
                timestamp=ist_now,
            )
        db.add(log_action)
        db.commit()

        return {
             "city":{
                "city_name": property_obj.area.sublocation.city.city_name if property_obj.area and property_obj.area.sublocation else None,
            },
            "sublocation":{
                "sublocation_name": property_obj.area.sublocation.sublocation_name if property_obj.area else None,
            },
            "area":{
                "area_name": property_obj.area.area_name if property_obj.area else None,
            },
            "properties":{
                "project_name": property_obj.project_name,
                "building": property_obj.building,
                "address2": property_obj.address2,
                "description": property_obj.descriptions.description,
                "pin": property_obj.pin,
                "company": property_obj.company,
                "status_code": property_obj.status_code,
                "property_type": property_obj.property_type,
                "c_status": property_obj.c_status,
                "lease_type": property_obj.lease_sales.lease_type,
                "usp": property_obj.usp,
            },
            "property_details": property_detail_list,
            "contacts": [
                    {"contact_person": contact.contact_person, "email": contact.email, "mobile": contact.mobile,  "contact_person_address": contact.contact_person_address}
                    for contact in detail.contacts
                ]
           
        }
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while fetch property hierarchy data.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetch property hierarchy data") #f"An unexpected error occurred: {str(e)}"


@router.put("/update_property_details_with_hierarchy/{property_id}", response_model=None)
async def update_property_hierarchy(
    property_id: str,
    property_data: CityUpdateSchema,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property_obj = db.query(Property).filter(Property.property_code == property_id).first()

        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        if property_data.city_name:
            city = db.query(City).filter(City.city_name == property_data.city_name).first()
            if not city:
                city = City(city_name=property_data.city_name)
                db.add(city)
                db.commit()
            property_obj.city = city.city_name
        
        for sublocation_data in property_data.sublocations:
            sublocation = db.query(Sublocation).filter(Sublocation.sublocation_name == sublocation_data.sublocation_name).first()
            if sublocation:
                for area_data in sublocation_data.areas:
                    area = db.query(Area).filter(Area.area_name == area_data.area_name).first()
                    if area:
                        for property_data in area_data.properties:
                            if property_obj.building == property_data.building:  
                                if property_data.building:
                                    property_obj.building = property_data.building
                                if property_data.address2:
                                    property_obj.address2 = property_data.address2
                                if property_data.description:
                                    description = db.query(Description).filter(Description.des_id == property_obj.des_code).first()
                                    if description:
                                        description.description = property_data.description
                                if property_data.status_code:
                                    property_obj.status_code = property_data.status_code
                                if property_data.property_type:
                                    property_obj.property_type = property_data.property_type
                                if property_data.lease_type:
                                    lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == property_obj.lease_code).first()
                                    if lease_sale:
                                        lease_sale.lease_type = property_data.lease_type
                                if property_data.usp:
                                    property_obj.usp = property_data.usp
                                if property_data.project_name: 
                                    property_obj.project_name = property_data.project_name
                                    
                                # Update property details
                                for detail_data in property_data.property_details:
                                    property_detail = db.query(PropertyDetails).filter(PropertyDetails.property_code == property_id).first()
                                    if property_detail:
                                        if detail_data.floor:
                                            property_detail.floor = detail_data.floor
                                        if detail_data.unit_no:
                                            property_detail.unit_no = detail_data.unit_no
                                        if detail_data.wing:
                                            property_detail.wing = detail_data.wing
                                        if detail_data.car_parking:
                                            property_detail.car_parking = detail_data.car_parking
                                        if detail_data.rate_buy:
                                            property_detail.rate_buy = detail_data.rate_buy
                                        if detail_data.rate_lease:
                                            property_detail.rate_lease = detail_data.rate_lease
                                        if detail_data.remarks:
                                            property_detail.remarks = detail_data.remarks

                                        # Update contacts
                                        for contact_data in detail_data.contacts:
                                            contact = db.query(PropertyContacts).filter(PropertyContacts.property_detail_id == property_detail.id).first()
                                            if contact:
                                                if contact_data.contact_person:
                                                    contact.contact_person = contact_data.contact_person
                                                if contact_data.email:
                                                    contact.email = contact_data.email
                                                if contact_data.mobile:
                                                    contact.mobile = contact_data.mobile
                                                if contact_data.contact_person_address:  
                                                    contact.contact_person_address = contact_data.contact_person_address
        
         # Log the creation action
        log_action=Logs(
            user_id=current_user.user_id,
            action="updated all property hierarchy data ",
            property_id=property_id,
        )
        db.add(log_action)
    
        db.commit()
        return {"message": "Property hierarchy updated successfully"}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while  updating property hierarchy data.")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating property hierarchy data")




@router.delete("/delete_property_hierarchy/{property_id}", response_model=None)
async def delete_property_hierarchy(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: AriyanspropertiesUser = Depends(get_current_user)
):
    try:
        property_details = db.query(PropertyDetails).filter(PropertyDetails.property_code == property_id).first()
        if not property_details:
            raise HTTPException(status_code=404, detail="Property not found")
        
         # Log the creation action
        log_action=Logs(
            user_id=current_user.user_id,
            action="Deleted all property hierarchy data",
            property_id=property_id,
        )
        db.add(log_action)
        db.commit()

        db.query(PropertyContacts).filter(PropertyContacts.property_detail_id == property_details.id).delete(synchronize_session=False)

        db.delete(property_details)

        property_obj = db.query(Property).filter(Property.property_code == property_id).first()
        db.delete(property_obj)

        sublocation_obj = db.query(Sublocation).join(Area).join(Property).filter(Property.property_code == property_id).first()
        area_obj = db.query(Area).join(Property).filter(Property.property_code == property_id).first()
        city_obj = db.query(City).join(Sublocation).join(Area).join(Property).filter(Property.property_code == property_id).first()

        if not db.query(Property).filter(Property.area_id == area_obj.area_id).first():
            db.delete(area_obj)

        if not db.query(Area).filter(Area.sublocation_id == sublocation_obj.sublocation_id).first():
            db.delete(sublocation_obj)

        if not db.query(Sublocation).filter(Sublocation.city_id == city_obj.city_id).first():
            db.delete(city_obj)

        db.commit()

        return {"message": "Property and associated hierarchy deleted successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while  deleting property hierarchy data.")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting property hierarchy data")