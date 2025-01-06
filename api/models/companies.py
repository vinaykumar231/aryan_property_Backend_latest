from sqlalchemy import Column, Float, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Companies Table (1, 'Tech Solutions Inc.', 'John Doe', '1234 Tech Street, Silicon Valley, CA 94043'),
class Companies(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100))
    contact_person = Column(String(100))
    address = Column(String(200))