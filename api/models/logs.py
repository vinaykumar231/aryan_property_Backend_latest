from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Logs Table  1, 'P123', 'Added Property', '2025-01-06 10:30:00'
class Logs(Base):
    __tablename__ = "logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    property_id = Column(String(50), ForeignKey("property.property_code", ondelete="CASCADE"))
    action = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("AriyanspropertiesUser", back_populates="logs")
    property = relationship("Property", back_populates="logs")
   
    