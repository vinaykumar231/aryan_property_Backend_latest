from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class FurnishedProperty(Base):
    __tablename__ = "furnished_properties__tb"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    #property_code = Column(String(50), ForeignKey("property.property_code"))
    des_code = Column(String(50), ForeignKey("descriptions.des_id")) 
    workstations = Column(Integer, default=0)
    workstation_type_cubicle = Column(Boolean, default=False)
    workstation_type_linear = Column(Boolean, default=False)
    workstation_type_both = Column(Boolean, default=False)
    
    cabins = Column(Integer, default=0)
    meeting_rooms = Column(Integer, default=0)
    conference_rooms = Column(Integer, default=0)
    cafeteria_seats = Column(Integer, default=0)
    washrooms = Column(Integer, default=0)
    
    pantry_area = Column(Boolean, default=False)
    backup_ups_room = Column(Boolean, default=False)
    server_electrical_room = Column(Boolean, default=False)
    reception_waiting_area = Column(Boolean, default=False)

    edit_date = Column(DateTime, default=datetime.utcnow)

    description = relationship("Description", back_populates="furnished_properties")
    property = relationship("Property", back_populates="furnished_properties")
    


    
