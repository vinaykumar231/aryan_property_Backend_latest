
from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# 'P123', 1000000, 5000, 10, '10A', 'East Wing', '2 slots', 'Spacious and well-lit', '2025-01-06', 1

class PropertyDetails(Base):
    __tablename__ = "property_details"
    id = Column(Integer, primary_key=True, index=True)
    property_code = Column(String(50), ForeignKey("property.property_code"))
    rate_buy = Column(Float)
    rate_lease = Column(Float)
    floor = Column(Integer)
    unit_no = Column(String(50))
    wing = Column(String(50))
    car_parking = Column(String(50))
    remarks = Column(Text)
    edit_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    # Relationships
    user = relationship("AriyanspropertiesUser", back_populates="property_details")
    property = relationship("Property", back_populates="property_details")

