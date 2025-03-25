from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Area Table (1, 1, 'Corporate Park', '2025-01-06 12:00:00'),
class Area(Base):
    __tablename__ = "area"
    area_id = Column(Integer, primary_key=True, index=True)
    property_code = Column(String(50), ForeignKey("property.property_code"))
    filter_area_id = Column(Integer, ForeignKey("filter_area.filter_area_id"))
    built_up_area = Column(Float)
    carpet_up_area = Column(Float)
    efficiency = Column(String(255), nullable=True) 
    car_parking = Column(String(100))
    rental_psf = Column(String(100))
    outright_rate_psf = Column(String(100))
    terrace_area =  Column(String(255), nullable=True) 
    remarks = Column(Text, nullable=True) 
    #floor_wing_unit_id = Column(Integer, ForeignKey("floor_wing_unit.floor_wing_unit_id"))
    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    property = relationship("Property", back_populates="area")
    filter_area = relationship("FilterArea", back_populates="area_list")
    floor_wing_unit_number = relationship("Floor_wing_unit", back_populates="area")
