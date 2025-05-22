from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    role: str

    class Config:
        orm_mode = True

class UserOut(UserCreate):
    id: int

    class Config:
        orm_mode = True
