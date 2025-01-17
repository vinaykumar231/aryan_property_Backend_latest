from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# LeaseSale Table  ('L001', 'Long-term Lease', '2025-01-06 12:00:00'),
class LeaseSale(Base):
    __tablename__ = "lease_sale"
    lease_id = Column(String(50), primary_key=True, index=True)
    #property_code = Column(String(50), ForeignKey("property.property_code"))
    lease_type = Column(String(50))
    edit_date = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="lease_sales")
    