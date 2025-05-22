from sqlalchemy import Column, Integer, String
from app.database import Base

class AuthUser(Base):
    __tablename__ = "auth_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
