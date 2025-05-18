from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="open")  # open, in_progress, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = Column(String)  # Stores username from auth service