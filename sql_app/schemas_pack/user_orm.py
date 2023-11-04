from .base import *


class UserBase(BaseModel):
    phone: str = ''
    email: str = ''


class UserCreate(UserBase):
    password: str
    id: str


class User(UserBase):
    id: str

    class Config:
        orm_mode = True
