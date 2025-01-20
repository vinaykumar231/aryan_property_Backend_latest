from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# PropertyTypes Table:  1 ,Commercial,'2025-01-06 10:30:00'
class PropertyTypes(Base):
    __tablename__ = "property_types"
    type_id = Column(String(50), primary_key=True, index=True)
    category = Column(String(100))  #  'Commercial',Industrial' 'Retail','Office Space','Hospitality',
    edit_date = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="property_types")
   