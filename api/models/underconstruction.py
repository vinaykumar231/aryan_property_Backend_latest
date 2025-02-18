# from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from database import Base
# from datetime import datetime

# # Underconstruction Table  (2025, 'DESC123', '2025-01-06 12:00:00'),
# class Underconstruction(Base):
#     __tablename__ = "underconstruction"
#     uc_id = Column(Integer, primary_key=True, index=True)
#     property_code = Column(String(50), ForeignKey("property.property_code"))
#     year = Column(Integer)
#     des_id = Column(String(50), ForeignKey("descriptions.des_id"))
#     edit_date = Column(DateTime, default=datetime.utcnow)

#     property = relationship("Property", back_populates="underconstructions")
#     description = relationship("Description", back_populates="underconstructions")
