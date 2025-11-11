from pathlib import Path
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, joinedload
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

# Use SQLite with local database file in swagger_server/database directory
db_dir = Path(__file__).parent / 'database'
db_dir.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{db_dir / 'library.db'}"

# Create SQLite engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

LocalSession = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


# --- MODELS ---
class Book(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True)
    book_name = Column(String, nullable=False)
    author = Column(String, nullable=False)

    copies = relationship("BookCopy", back_populates="book")


class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    is_borrowed = Column(Boolean, default=False, nullable=False)

    book = relationship("Book", back_populates="copies")
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


# --- INITIALIZE DATABASE ---
Base.metadata.create_all(bind=engine)
