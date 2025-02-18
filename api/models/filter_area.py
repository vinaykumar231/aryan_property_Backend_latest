from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Area Table (1, 1, 'Corporate Park', '2025-01-06 12:00:00'),
class FilterArea(Base):
    __tablename__ = "filter_area"
    filter_area_id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String(100), nullable=True)  #Corporate Park, Business Hub, Office Towers, Tech Zone, Commercial Plaza. Central Business Center
    edit_date = Column(DateTime, default=datetime.utcnow)

    area_list = relationship("Area", back_populates="filter_area")
    
    


