from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Description(Base):
    __tablename__ = "descriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    des_id = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    edit_date = Column(DateTime, default=datetime.utcnow)

    
    property = relationship("Property", back_populates="descriptions")
    furnished_properties = relationship("FurnishedProperty", back_populates="description")
    
