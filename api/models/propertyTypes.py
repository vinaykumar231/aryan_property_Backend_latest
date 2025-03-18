from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
#from furnished_property import FurnishedProperty

# PropertyTypes Table:  1 ,Commercial,'2025-01-06 10:30:00'
class PropertyTypes(Base):
    __tablename__ = "property_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(100))  #  'Commercial',Industrial' 'Retail','Office Space','Hospitality',
    edit_date = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="property_types")
    
   