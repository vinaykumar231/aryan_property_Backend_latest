from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Area Table (1, 1, 'Corporate Park', '2025-01-06 12:00:00'),
class Area(Base):
    __tablename__ = "area"
    area_id = Column(Integer, primary_key=True, index=True)
    sublocation_id = Column(Integer, ForeignKey("sublocation.sublocation_id"))
    area_name = Column(String(100))  #Corporate Park, Business Hub, Office Towers, Tech Zone, Commercial Plaza. Central Business Center
    edit_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sublocation = relationship("Sublocation", back_populates="areas")
    property = relationship("Property", back_populates="area")
