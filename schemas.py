from pydantic import BaseModel, Field, validator
from typing import Optional
import datetime
import re

class UserBase(BaseModel):
    name: str
    username: str

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class MembershipBase(BaseModel):
    name: str
    address: str
    phone: str
    duration: str

class MembershipCreate(MembershipBase):
    pass

class BookBase(BaseModel):
    name: str
    author: str
    serial_number: str
    category: str
    type: str = "Book"

class BookCreate(BookBase):
    pass

class TransactionBase(BaseModel):
    book_id: int
    user_id: int
    issue_date: datetime.date
    return_date: datetime.date

class TransactionCreate(TransactionBase):
    pass
