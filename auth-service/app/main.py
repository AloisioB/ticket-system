from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
import httpx

app = FastAPI()

SECRET_KEY = "your-strong-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def verify_user_credentials(username: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/users/verify",
            json={"username": username, "password": password}
        )
        return response.status_code == 200

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not await verify_user_credentials(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = jwt.encode(
        {"sub": form_data.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}