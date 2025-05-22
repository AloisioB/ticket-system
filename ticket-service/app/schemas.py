from pydantic import BaseModel
from typing import Optional

# Shared base
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "open"

# Schema for creating a ticket
class TicketCreate(TicketBase):
    pass

# Schema for updating a ticket
class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Schema for returning a ticket
class TicketOut(TicketBase):
    id: int

    class Config:
        orm_mode = True
