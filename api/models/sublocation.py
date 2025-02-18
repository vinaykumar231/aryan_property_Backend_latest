# from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from database import Base
# from datetime import datetime


# # Sublocation Table  (1, 'Old Town or link road', '2025-01-06 12:00:00');
# class Sublocation(Base):
#     __tablename__ = "sublocation"
#     sublocation_id = Column(Integer, primary_key=True, index=True)
#     city_id = Column(Integer, ForeignKey("city.city_id"))
#     sublocation_name = Column(String(100))
#     edit_date = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     city = relationship("City", back_populates="sublocations")
#     areas = relationship("Area", back_populates="sublocation")