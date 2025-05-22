from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    email: EmailStr
    password: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
