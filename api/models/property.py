
from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey
from sqlalchemy.orm import relationship
from api.models.description import Description
from database import Base
from datetime import datetime


# Property Table  P123', 'Skyline Tower', '2nd Avenue', 'New York', 'Manhattan', '10001', 'RealtyCorp', 'Available', 1, 'Active', L342, D124, 'Prime Location');
class Property(Base):
    __tablename__ = "property"
    property_code = Column(String(50), primary_key=True, index=True)
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
    des_code = Column(String(50), ForeignKey("description.des_id"))
    usp = Column(String(255))  #(unique sell point) Prime Location, near metro station

    # Relationships
    property_details = relationship("PropertyDetails", back_populates="property")
    descriptions = relationship("Description", back_populates="property", foreign_keys=[Description.property_id])
    contacts = relationship("PropertyContacts", back_populates="property")
