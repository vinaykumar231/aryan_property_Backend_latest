from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime



# 1, 'A luxurious 2-bedroom apartment with stunning city views,'P123', '2025-01-06 10:30:00'.

class Description(Base):
    __tablename__ = "descriptions"
    des_id = Column(String(50), primary_key=True, index=True)
    description = Column(Text)
    #property_id = Column(String(50), ForeignKey("property.property_code"))
    edit_date = Column(DateTime, default=datetime.utcnow)

    # Specify the foreign key explicitly for the 'property' relationship
    property = relationship("Property", back_populates="descriptions")
    underconstructions = relationship("Underconstruction", back_populates="description")
