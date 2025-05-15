from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session  # Add this import
from jose import JWTError, jwt
import models, database
from database import SessionLocal, engine
from pydantic import BaseModel
import os
from typing import List

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TicketCreate(BaseModel):
    title: str
    description: str

async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

@app.post("/tickets/")
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),  # Now properly typed
    username: str = Depends(get_current_user)
):
    db_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        owner=username
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket



@app.get("/tickets/", response_model=List[TicketCreate])
async def list_tickets(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    tickets = db.query(models.Ticket).filter(models.Ticket.owner == username).all()
    return tickets


@app.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket or ticket.owner != username:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

@app.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket or ticket.owner != username:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket_data.title:
        ticket.title = ticket_data.title
    if ticket_data.description:
        ticket.description = ticket_data.description

    db.commit()
    db.refresh(ticket)
    return ticket


@app.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket or ticket.owner != username:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket deleted"}


@app.get("/tickets/search/")
async def search_tickets(
    keyword: str,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    results = db.query(models.Ticket).filter(
        models.Ticket.owner == username,
        (models.Ticket.title.ilike(f"%{keyword}%") |
         models.Ticket.description.ilike(f"%{keyword}%"))
    ).all()
    return results


