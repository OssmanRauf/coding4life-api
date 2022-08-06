from unittest.mock import Base
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from requests import request


# Base user Schema
class UserBase(BaseModel):
    email: Optional[EmailStr]
    username: Optional[str]
    name: Optional[str] = None
    description: Optional[str]
    # EmailStr


class UserUpdate(UserBase):
    pass


# Schema for user creation
class UserCreate(UserBase):
    password: str


# schema to return to user in creation
class User(UserBase):
    id: Optional[int]
    created_at: Optional[datetime]
    is_admin: Optional[bool] = False
    is_super_user: Optional[bool] = False

    class Config:
        orm_mode = True


# Schema for inside without password
class UserIn(BaseModel):
    id: int
    created_at: datetime
    password: str

# Schema for inside without password


class UserOut(UserBase):
    # profile_url: str
    id: int

    class Config:
        orm_mode = True


class Request(BaseModel):
    id: Optional[int]
    user_id: Optional[int]
    requested_at: Optional[datetime]

    class Config:
        orm_mode = True


class AdminRequests(BaseModel):
    AdminRequest: Optional[Request]
    User: Optional[User]

    class Config:
        orm_mode = True


class RequestAnswer(BaseModel):
    id: Optional[int]

    class Config:
        orm_mode = True
