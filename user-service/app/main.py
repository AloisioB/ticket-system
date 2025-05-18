from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from pydantic import BaseModel
from passlib.context import CryptContext  # Correct import

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password
    hashed_password = pwd_context.hash(user.password)
    
    # Create user
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/users/verify")
async def verify_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.verify_password(password):
        return {"valid": False}
    return {"valid": True}


from typing import List

class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

@app.get("/users/", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return
