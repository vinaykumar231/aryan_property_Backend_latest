# from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from database import Base
# from datetime import datetime

# # City Table (1, 'New York', '2025-01-06 12:00:00'),
# class City(Base):
#     __tablename__ = "city"
#     city_id = Column(Integer, primary_key=True, index=True)
#     city_name = Column(String(100)) # New York,Los Angeles, San Francisc, Chicago, Boston
#     edit_date = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     sublocations = relationship("Sublocation", back_populates="city")