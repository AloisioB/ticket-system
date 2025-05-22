from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx

from app.database import SessionLocal, engine, Base

from app import models
from app.schemas import UserCreate, UserOut

app = FastAPI()
security = HTTPBearer()

# Create DB tables
Base.metadata.create_all(bind=engine)

# Auth service endpoint
AUTH_SERVICE_URL = "http://localhost:8001/validate"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def validate_token(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(AUTH_SERVICE_URL, headers=headers)
    print("Auth Service Response:", response.status_code, response.text)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Invalid token")
    return response.json()


@app.post("/users", response_model=UserOut)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", response_model=list[UserOut])
async def list_users(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    await validate_token(credentials.credentials)
    return db.query(models.User).all()


@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    await validate_token(credentials.credentials)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
