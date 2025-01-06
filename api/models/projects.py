from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Projects Table (1, 'Downtown Office Complex', 'P123', 'A modern office building in the heart of downtown with all the latest amenities.', '150 slots');
class Projects(Base):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100))
    location = Column(String(50), ForeignKey("property.property_code"))
    description = Column(Text)
    car_parking = Column(String(50))  # "150 slots (underground parking)", "150 slots (covered)", "150 outdoor parking slots"