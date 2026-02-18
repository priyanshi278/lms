from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True, index=True)
    membership_number = Column(String, unique=True, index=True)
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    start_date = Column(Date)
    expiry_date = Column(Date)
    duration = Column(String)

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    author = Column(String)
    serial_number = Column(String, unique=True, index=True)
    category = Column(String)
    status = Column(String)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    issue_date = Column(Date)
    return_date = Column(Date)
    actual_return_date = Column(Date, nullable=True)
    fine_amount = Column(Float, default=0.0)
    fine_paid = Column(Boolean, default=False)
    status = Column(String)
    remarks = Column(String, nullable=True)
    
    book = relationship("Book")
    user = relationship("User")
