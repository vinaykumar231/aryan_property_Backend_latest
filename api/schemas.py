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
    project_name:Optional[str] = None
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
    area_id:Optional[int] = None
    usp: Optional[str] = None  

class PropertyUpdate(BaseModel):
    project_name:Optional[str] = None
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
    area_id:Optional[int] = None
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
    # property_id: str

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
    property_detail_id:str
    contact_person: str
    email: EmailStr
    mobile: str
    contact_person_address:str

class PropertyContactCreate(PropertyContactBase):
    pass

class PropertyContactUpdate(BaseModel):
    property_id: Optional[str]
    contact_person: Optional[str]
    email: Optional[EmailStr]
    mobile: Optional[str]
    contact_person_address:Optional[str]

    class Config:
        orm_mode = True

###########################################  city #############################################################

class CityBase(BaseModel):
    city_name: str

class CityCreate(CityBase):
    pass

class CityUpdate(CityBase):
    pass

class CityResponse(CityBase):
    city_id: int
    edit_date: datetime

    class Config:
        orm_mode = True

########################################## sublocation ###########################################################

class SublocationCreate(BaseModel):
    city_id: int 
    sublocation_name: str  

class SublocationUpdate(BaseModel):
        sublocation_name: Optional[str]

class SublocationResponse(BaseModel):
        sublocation_id: int 
        city_id: int 
        sublocation_name: str  
        edit_date: datetime  

        class Config:
            orm_mode = True

############################################ area ###################################################################

class AreaCreate(BaseModel):
    sublocation_id: int
    area_name: str

class AreaUpdate(BaseModel):
    area_name: str

class AreaResponse(BaseModel):
    area_id: int
    sublocation_id: int
    area_name: str
    edit_date: datetime

    class Config:
        orm_mode = True

####################################################### company ################################################

class CompanyCreate(BaseModel):
    company_name: str
    contact_person: str
    address: str

class CompanyUpdate(BaseModel):
    company_name: str
    contact_person: str
    address: str

class CompanyResponse(BaseModel):
    company_id: int
    company_name: str
    contact_person: str
    address: str

    class Config:
        orm_mode = True


##############################################  underconstruction ###########################################

class UnderconstructionCreate(BaseModel):
    property_code: str
    year: int
    des_id: str
    

class UnderconstructionUpdate(BaseModel):
    property_code: str
    year: int
    des_id: str

class UnderconstructionResponse(BaseModel):
    uc_id: int
    year: int
    des_id: str
    edit_date: datetime

    class Config:
        orm_mode = True

#########################   Hirarchy create := City → Sublocation → Area → Property → PropertyDetails → PropertyContacts. ################


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
    address: str
    pin: str
    company: str
    status_code: str  # Active, Inactive, Sold, etc.
    property_type: str  # Residential, Commercial, etc.
    c_status: str  # Occupied, Lease, Available, etc.
    usp: Optional[str] = None  # Unique Selling Point
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

    class Config:
        orm_mode = True

############################################## property hierarchy data ###################################

class PropertyContactSchema(BaseModel):
    contact_person: str
    email: str
    mobile: str
    contact_person_address: Optional[str]

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
    project_name: str  # Added project_name field
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

###########################################

class PropertyContactUpdateSchema(BaseModel):
    contact_person: Optional[str]
    email: Optional[str]
    mobile: Optional[str]
    contact_person_address: Optional[str]

class PropertyDetailUpdateSchema(BaseModel):
    floor: Optional[int]
    unit_no: Optional[str]
    wing: Optional[str]
    car_parking: Optional[str]
    rate_buy: Optional[float]
    rate_lease: Optional[float]
    remarks: Optional[str]
    contacts: Optional[List[PropertyContactUpdateSchema]]  

class PropertyUpdateSchema(BaseModel):
    project_name: Optional[str]
    building: Optional[str]
    address2: Optional[str]
    description: Optional[str]
    area: Optional[str]
    pin: Optional[str]
    company: Optional[str]
    status_code: Optional[str]
    property_type: Optional[str]
    c_status: Optional[str]
    lease_type: Optional[str]
    usp: Optional[str]
    property_details: Optional[List[PropertyDetailUpdateSchema]]  
class AreaUpdateSchema(BaseModel):
    area_name: Optional[str]  
    properties: Optional[List[PropertyUpdateSchema]]  

class SublocationUpdateSchema(BaseModel):
    sublocation_name: Optional[str] 
    areas: Optional[List[AreaUpdateSchema]]  

class CityUpdateSchema(BaseModel):
    city_name: Optional[str]  
    sublocations: Optional[List[SublocationUpdateSchema]]  

    class Config:
        orm_mode = True

   
