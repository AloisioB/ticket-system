from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app import models, schemas, auth
from app.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)   

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", tags=["Auth"])
def register(user: schemas.RegisterUser, db: Session = Depends(get_db)):
    existing_user = db.query(models.AuthUser).filter(models.AuthUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user.password)
    new_user = models.AuthUser(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.AuthUser).filter(models.AuthUser.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/validate", tags=["Auth"])
def validate_token(token: str = Depends(oauth2_scheme)):
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"email": payload.get("sub")}
