from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Area Table (1, 1, 'Corporate Park', '2025-01-06 12:00:00'),
class Floor_wing_unit(Base):
    __tablename__ = "floor_wing_unit"

    floor_wing_unit_id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("area.area_id"))
    wing = Column(String(100), nullable=True)
    floor = Column(String(100), nullable=True)
    unit_number = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    area = relationship("Area", back_populates="floor_wing_unit_number")
   