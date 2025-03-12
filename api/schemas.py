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
    building_name: str
    full_address: str
    sublocation: str
    city: str
    des_code: str
    LL_outright: str
    property_type: str
    poss_status: str
    Reopen_date: Optional[str] = None
    east_west: Optional[str] = None

class PropertyUpdate(BaseModel):
    project_name: Optional[str] = None
    building: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    pin: Optional[str] = None
    company: Optional[str] = None
    status_code: Optional[str] = None
    property_type: Optional[str]
    c_status: Optional[str] = None
    lease_code: Optional[str] = None
    des_code: Optional[str] = None
    area_id: Optional[int] = None
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
    builtup:float
    carpet:float

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


############################################## property hierarchy data ###################################

# Pydantic Models with corrected field names and validations
class PropertyContactSchema(BaseModel):
    company_builder_name: str
    address: str
    conatact_person_1: Optional[str] = None  
    conatact_person_2: Optional[str] = None  
    conatact_person_number_1: Optional[int] = None  
    conatact_person_number_2: Optional[int] = None  
    email: str
    reffered_by: Optional[str] = None  

class UnitFloorWingSchema(BaseModel):
    wing: Optional[str] = None
    floor: Optional[str] = None
    unit_number: Optional[str] = None

class AreaSchema(BaseModel):
    filter_area_id: int
    built_up_area: float
    carpet_up_area: float
    efficiency: Optional[str] = None
    car_parking: Optional[str] = None
    rental_psf: Optional[str] = None
    outright_rate_psf: Optional[str] = None
    unit_floor_wing: List[UnitFloorWingSchema]
    contacts: List[PropertyContactSchema]

class PropertySchema(BaseModel):
    furnished_property_id:Optional[int] = None
    building_name: str
    full_address: str
    sublocation: Optional[str] = None
    #location: Optional[str] = None
    city: str
    des_code: str
    LL_outright: str
    property_type: str
    poss_status: Optional[str] = None
    east_west: Optional[str] = None
    #availability: Optional[str] = None
    #lease_out: Optional[str] = None
    reopen_date: Optional[str] = None
    #sold_out: Optional[str] = None
    areas: List[AreaSchema]

    class Config:
        orm_mode = True

#################################### client #####################

# Pydantic model for request and response
class ClientCreate(BaseModel):
    Name: str
    Emial: str
    Conatct_Number: str
    Location: str

    class Config:
        from_attributes = True


################################## FurnishedProperty ###########################

class FurnishedPropertyCreate(BaseModel):
    #property_code:str
    des_code: str
    workstations: Optional[int] = 0
    workstation_type_cubicle: Optional[bool] = False
    workstation_type_linear: Optional[bool] = False
    workstation_type_both: Optional[bool] = False
    cabins: Optional[int] = 0
    meeting_rooms: Optional[int] = 0
    conference_rooms: Optional[int] = 0
    cafeteria_seats: Optional[int] = 0
    washrooms: Optional[int] = 0
    pantry_area: Optional[bool] = False
    backup_ups_room: Optional[bool] = False
    server_electrical_room: Optional[bool] = False
    reception_waiting_area: Optional[bool] = False

class FurnishedPropertyUpdate(BaseModel):
    #property_code:Optional[str]=None
    des_code: Optional[str]=None
    workstations: Optional[int] = None
    workstation_type_cubicle: Optional[bool] = None
    workstation_type_linear: Optional[bool] = None
    workstation_type_both: Optional[bool] = None
    cabins: Optional[int] = None
    meeting_rooms: Optional[int] = None
    conference_rooms: Optional[int] = None
    cafeteria_seats: Optional[int] = None
    washrooms: Optional[int] = None
    pantry_area: Optional[bool] = None
    backup_ups_room: Optional[bool] = None
    server_electrical_room: Optional[bool] = None
    reception_waiting_area: Optional[bool] = None

    class Config:
        orm_mode = True

