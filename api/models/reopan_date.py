from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
#from furnished_property import FurnishedProperty

class Reopen(Base):
    __tablename__ = "reopan_tb1"

    #property_code = Column(String(50), ForeignKey("property.property_code"))
    id = Column(Integer, primary_key=True,index=True)
    availability = Column(String(100), nullable=True )
    lease_out = Column(String(100), nullable=True )
    reopen_date = Column(String(100), nullable=True )
    sold_out=Column(String(100), nullable=True)

    #properties = relationship("Property", back_populates="reopen")
    
   