from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Client(Base):
    __tablename__ = "clients_tb"

    client_id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(200))
    Emial = Column(String(100))
    Conatct_Number = Column(String(100))
    Location = Column(String(200))
    created_on = Column(DateTime, default=datetime.utcnow)

