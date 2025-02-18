from sqlalchemy import BigInteger, Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class PropertyContacts(Base):
    __tablename__ = "property_contacts1"
    contact_id = Column(Integer, primary_key=True, index=True)
    property_code = Column(String(50), ForeignKey("property.property_code"))
    company_builder_name = Column(String(100))
    address = Column(String(100))
    conatact_person_1 = Column(String(100),nullable=True)
    conatact_person_2 = Column(String(100), nullable=True)
    conatact_person_number_1 = Column(BigInteger, nullable=True)
    conatact_person_number_2 = Column(BigInteger, nullable=True)
    email = Column(String(100))
    reffered_by = Column(String(300))
    

    # Relationships
    property = relationship("Property", back_populates="contacts")
    
