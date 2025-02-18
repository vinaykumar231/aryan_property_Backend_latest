from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Description(Base):
    __tablename__ = "descriptions"
    des_id = Column(String(50), primary_key=True, index=True)
    description = Column(Text)
    edit_date = Column(DateTime, default=datetime.utcnow)

    
    property = relationship("Property", back_populates="descriptions")
    
