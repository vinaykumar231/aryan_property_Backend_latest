
from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey
from sqlalchemy.orm import relationship
from api.models.description import Description
from ..models.leaseSale import LeaseSale
from database import Base
from datetime import datetime
from sqlalchemy.orm import validates,Session
from database import SessionLocal


# Property Table  P123','Skyline Tower project', 'Skyline Tower', '2nd Avenue', 'New York', 'Manhattan', '10001', 'RealtyCorp', 'Available', 1, 'Active', L342, D124, 'Prime Location');
class Property(Base):
    __tablename__ = "property"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_code = Column(String(50), primary_key=True, index=True, unique=True,)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    project_name = Column(String(255))  
    building = Column(String(200))
    address2 = Column(String(200))
    city = Column(String(100))
    area = Column(String(100))
    pin = Column(String(10))
    company = Column(String(100))
    status_code = Column(String(50))  # Active, Inactive, Sold, Under Contract, Under Review
    property_type = Column(String(50), ForeignKey("property_types.type_id"))
    c_status = Column(String(50))  # Occupied, lease , available, Under Maintenance
    lease_code = Column(String(50), ForeignKey("lease_sale.lease_id"))
    des_code = Column(String(50), ForeignKey("descriptions.des_id"))
    area_id=Column(Integer, ForeignKey("area.area_id"))
    usp = Column(String(255))  #(unique sell point) Prime Location, near metro station
    edit_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    property_details = relationship("PropertyDetails", back_populates="property")
    descriptions = relationship("Description", back_populates="property")
    contacts = relationship("PropertyContacts", back_populates="property")
    user = relationship("AriyanspropertiesUser", back_populates="property")
    area = relationship("Area", back_populates="property")
    lease_sales = relationship("LeaseSale", back_populates="property")
    property_types = relationship("PropertyTypes", back_populates="property")
    logs = relationship("Logs", back_populates="property")
    underconstructions = relationship("Underconstruction", back_populates="property")
    
    

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