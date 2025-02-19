
from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey
from sqlalchemy.orm import relationship
from api.models.description import Description
from ..models.leaseSale import LeaseSale
from database import Base
from datetime import datetime
from sqlalchemy.orm import validates,Session
from database import SessionLocal


class Property(Base):
    __tablename__ = "property"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_code = Column(String(50), primary_key=True, index=True, unique=True,)
    user_id = Column(Integer, ForeignKey("users.user_id"))  
    building_name = Column(String(200))
    full_address = Column(String(200))
    sublocation = Column(String(200))
    # location = Column(String(200))
    city = Column(String(100))
    des_code = Column(String(50), ForeignKey("descriptions.des_id"))
    LL_outright = Column(String(100))
    property_type = Column(String(50), ForeignKey("property_types.type_id"))
    poss_status = Column(String(50)) 
    Reopen_date = Column(String(100))
    east_west=  Column(String(50)) 
    created_date = Column(DateTime, default=datetime.utcnow)

 
   
    # Relationships
    descriptions = relationship("Description", back_populates="property")
    contacts = relationship("PropertyContacts", back_populates="property")
    user = relationship("AriyanspropertiesUser", back_populates="property")
    area = relationship("Area", back_populates="property")
    #lease_sales = relationship("LeaseSale", back_populates="property")
    property_types = relationship("PropertyTypes", back_populates="property")
    logs = relationship("Logs", back_populates="property")
    #reopen = relationship("Reopen", back_populates="properties")
    

    @validates('property_code')
    def validate_property_code(self, key, value):
        if value is None:  
            value = f"P{str(self.id).zfill(3)}"  
        return value
    
def generate_property_code(db: Session):
    last_property = db.query(Property).order_by(Property.property_code.desc()).first()
    if last_property:
        last_code = int(last_property.property_code[1:]) 
        new_code = f"P{str(last_code + 1).zfill(3)}"
    else:
        new_code = "P001"
    return new_code