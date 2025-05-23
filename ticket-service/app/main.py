from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx

from app.database import SessionLocal, engine
from app.schemas import TicketCreate, TicketUpdate, TicketOut

from app import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Auth Service validation URL
AUTH_SERVICE_URL = "http://auth-service:8000/validate"

# Security scheme
security = HTTPBearer()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to validate JWT with Auth Service
async def validate_token(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(AUTH_SERVICE_URL, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    return response.json()

# Create a ticket
@app.post("/tickets", response_model=TicketOut)
async def create_ticket(
    ticket: TicketCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    await validate_token(credentials.credentials)
    db_ticket = models.Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# List all tickets
@app.get("/tickets", response_model=list[TicketOut])
async def list_tickets(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    await validate_token(credentials.credentials)
    return db.query(models.Ticket).all()


# Update a ticket
@app.put("/tickets/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    await validate_token(credentials.credentials)
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket_data.dict(exclude_unset=True).items():
        setattr(ticket, key, value)
    db.commit()
    db.refresh(ticket)
    return ticket


# Delete a ticket
@app.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    await validate_token(credentials.credentials)
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket deleted"}

