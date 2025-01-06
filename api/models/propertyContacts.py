from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

#  ('P123', 'John Doe', 'johndoe@example.com', '1234567890'),
class PropertyContacts(Base):
    __tablename__ = "property_contacts"
    contact_id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String(50), ForeignKey("property.property_code"))
    contact_person = Column(String(100))
    email = Column(String(100))
    mobile = Column(String(15))

    # Relationships
    property = relationship("Property", back_populates="contacts")
