from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

#  ('P123', 'John Doe', 'johndoe@example.com', '1234567890'),
class PropertyContacts(Base):
    __tablename__ = "property_contacts"
    contact_id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String(50), ForeignKey("property.property_code"))
    property_detail_id = Column(Integer, ForeignKey('property_details.id'))
    contact_person = Column(String(100))
    email = Column(String(100))
    mobile = Column(String(15))
    contact_person_address=Column(Text)

    # Relationships
    property = relationship("Property", back_populates="contacts")
    property_detail = relationship("PropertyDetails", back_populates="contacts")
    property_detail = relationship("PropertyDetails", back_populates="contacts")
