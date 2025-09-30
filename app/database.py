from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import datetime
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import time

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# postgresql://user:password@host:port/dbname
# DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
# Instead of localhost
DATABASE_URL = "postgresql://postgres:postgres@db:5432/mydb"

for i in range(10):
    try:
        engine = engine.create_engine(DATABASE_URL)
        engine.connect()
        break
    except Exception as e:
        print("Waiting for Postgres...")
        time.sleep(2)

LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True)
    book_name = Column(String, nullable=False)
    author = Column(String, nullable=False)

    copies = relationship("BookCopy", back_populates="book") # Points to BookCopy.book

class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)

    is_borrowed = Column(Boolean, default=False, nullable=False)

    book = relationship("Book", back_populates="copies") # Points to Book.copies
    borrows = relationship("Borrow", back_populates="copy")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)

    borrows = relationship("Borrow", back_populates="user")

class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=False)

    start_date = Column(DateTime, default=datetime.date.today)
    end_date = Column(DateTime)

    user = relationship("User", back_populates="borrows")
    copy = relationship("BookCopy", back_populates="borrows")
    
# Objects
# - book
#   + book_name
#   + book_id (PK)
# - book_copy:
#   + copy_id (PK)
#   + book_id (FK)
#   + is_borrowed
# - user:
#   + user_id (PK)
#   + user_name
# - borrow: 
#   + borrow_id (PK)
#   + user_id (FK)
#   + book_id (FK)
#   + borrow_date
#   + end_date