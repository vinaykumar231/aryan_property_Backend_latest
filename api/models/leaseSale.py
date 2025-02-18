from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class LeaseSale(Base):
    __tablename__ = "lease_sale"
    lease_id = Column(String(50), primary_key=True, index=True)
    lease_type = Column(String(50),nullable=True)
    edit_date = Column(DateTime, default=datetime.utcnow)

    #property = relationship("Property", back_populates="lease_sales")
    