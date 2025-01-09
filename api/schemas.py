from pydantic import BaseModel,  Field, EmailStr, validator
from typing import Optional, List
from fastapi import UploadFile, File
from datetime import date, datetime
from enum import Enum
from sqlalchemy import JSON
import re


######################################## User logiin and register #############################
class LoginInput(BaseModel):
    email: str
    user_password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    class Config:
        from_attributes = True


class UserType(str, Enum):
    admin = "admin"
    user = "user"
   
   
   
class UserCreate(BaseModel):
    user_name: str
    user_email: str
    user_password: str
    user_type: UserType = UserType.user
    phone_no: str

    class Config:
        from_attributes = True


class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    phone_no: Optional[int] = None
    user_type: Optional[str] = None
    current_password: Optional[str] = None

##########################################   Property   ####################################################

class PropertyCreate(BaseModel):
    building: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    pin: Optional[str] = None
    company: Optional[str] = None
    status_code: Optional[str] = None  
    property_type: Optional[str] = None
    c_status: Optional[str] = None  
    lease_code: Optional[str] = None
    des_code: Optional[str] = None
    usp: Optional[str] = None  

class PropertyUpdate(BaseModel):
    building: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    pin: Optional[str] = None
    company: Optional[str] = None
    status_code: Optional[str] = None
    property_type: Optional[str] = None
    c_status: Optional[str] = None
    lease_code: Optional[str] = None
    des_code: Optional[str] = None
    usp: Optional[str] = None
    
    class Config:
        orm_mode = True

################################### Property Details  ###########################

class PropertyDetailsBase(BaseModel):
    property_code: str
    rate_buy: float
    rate_lease: float
    floor: int
    unit_no: str
    wing: str
    car_parking: str
    remarks: str

class PropertyDetailsCreate(PropertyDetailsBase):
    pass

class PropertyDetailsResponse(PropertyDetailsBase):
    id: int
    edit_date: datetime

class PropertyDetailsUpdate(BaseModel):
    property_code: Optional[str] = None
    rate_buy: Optional[float] = None
    rate_lease: Optional[float] = None
    floor: Optional[int] = None
    unit_no: Optional[str] = None
    wing: Optional[str] = None
    car_parking: Optional[str] = None
    remarks: Optional[str] = None

    class Config:
        orm_mode = True

################################################  Property Type  #########################################################

class PropertyTypeCreate(BaseModel):
    category: str

class PropertyTypeUpdate(BaseModel):
    category: str

class PropertyTypeResponse(BaseModel):
    type_id: str
    category: str
    

    class Config:
        orm_mode = True

###################################################  Lease Sale  ###########################################################

from pydantic import BaseModel

class LeaseSaleCreate(BaseModel):
    lease_type: str

class LeaseSaleUpdate(BaseModel):
    lease_type: str

class LeaseSaleResponse(BaseModel):
    lease_id: str
    lease_type: str
    edit_date: str

    class Config:
        orm_mode = True

##############################################  Descriptions  ########################################################################

class DescriptionCreate(BaseModel):
    description: str
    property_id: str

class DescriptionUpdate(BaseModel):
    description: str

class DescriptionResponse(BaseModel):
    des_id: str
    description: str
    property_id: str
    edit_date: str

    class Config:
        orm_mode = True

############################################################   Property Contact ##########################################################

class PropertyContactBase(BaseModel):
    property_id: str
    contact_person: str
    email: EmailStr
    mobile: str

class PropertyContactCreate(PropertyContactBase):
    pass

class PropertyContactUpdate(BaseModel):
    property_id: Optional[str]
    contact_person: Optional[str]
    email: Optional[EmailStr]
    mobile: Optional[str]

    class Config:
        orm_mode = True