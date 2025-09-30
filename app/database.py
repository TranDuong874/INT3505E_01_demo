from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import datetime
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker

# postgresql://user:password@host:port/dbname
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mydb"

engine = engine.create_engine(DATABASE_URL, echo=True)

LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String, nullable=False)

    copies = relationship("BookCopy", back_populates="book") # Points to BookCopy.book

class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

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
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
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