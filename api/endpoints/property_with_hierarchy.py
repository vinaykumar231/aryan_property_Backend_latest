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
from api.models.property import Property, generate_property_code
from api.models.propertyContacts import PropertyContacts
from api.models.propertyDetails import PropertyDetails
from api.models.propertyTypes import PropertyTypes
from api.models.sublocation import Sublocation
from api.models.user import AriyanspropertiesUser
from auth.auth_bearer import get_current_user
from database import get_db

router = APIRouter()

class PropertyContactSchema(BaseModel):
    contact_person: str
    email: str
    mobile: str

class PropertyDetailSchema(BaseModel):
    floor: int
    unit_no: str
    wing: str
    car_parking: str
    rate_buy: float
    rate_lease: float
    remarks: str
    contacts: List[PropertyContactSchema]

class PropertySchema(BaseModel):
    building: str
    address2: str
    description: str
    area: str
    pin: str
    company: str
    status_code: str
    property_type: str
    c_status: str
    lease_type: Optional[str]
    usp: Optional[str]
    property_details: List[PropertyDetailSchema]

class AreaSchema(BaseModel):
    area_name: str
    properties: List[PropertySchema]

class SublocationSchema(BaseModel):
    sublocation_name: str
    areas: List[AreaSchema]

class CitySchema(BaseModel):
    city_name: str
    sublocations: List[SublocationSchema]

@router.post("/add_property_details_with_hierarchy/", response_model=None)
async def add_city(
    city_data: CitySchema, 
    db: AsyncSession = Depends(get_db), 
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
                city_id=city.city_id,  # Assume City has an ID field
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
                    # Generate unique property code
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
                        category=property_data.property_type,
                        edit_date=ist_now
                    )
                    db.add(property_type)
                    db.commit()

                    property_obj = Property(
                        property_code=property_code,
                        user_id=current_user.user_id,
                        building=property_data.building,
                        address2=property_data.address2,
                        city_id=city.city_id,
                        area_id=area.area_id,
                        pin=property_data.pin,
                        company=property_data.company,
                        status_code=property_data.status_code,
                        property_type=property_type.category,
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
                            property_id=property_obj.id
                        )
                        db.add(property_detail)
                        db.flush()

                        for contact_data in detail_data.contacts:
                            contact = PropertyContacts(
                                contact_person=contact_data.contact_person,
                                email=contact_data.email,
                                mobile=contact_data.mobile,
                                property_detail_id=property_detail.id
                            )
                            db.add(contact)

        db.commit()
        return {"message": "City and related hierarchy added successfully"}
    
    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
