from sqlalchemy import Column, Integer, String, Float, Boolean
from pydantic import BaseModel
from typing import Optional, List

from app.database.connection import Base
from app.models.hateoas_model import Link, PaginatedResponse


# SQLAlchemy ORM Model (for database)
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    isbn = Column(String, unique=True, nullable=True)
    in_stock = Column(Boolean, default=True)

class BookBase(BaseModel):
    title: str
    author: str
    price: Optional[float] = None
    isbn: Optional[str] = None
    in_stock: Optional[bool] = True

class BookCreate(BookBase):
    """Schema for creating a book"""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)"""
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    isbn: Optional[str] = None
    in_stock: Optional[bool] = None


class BookResponse(BookBase):
    """Schema for book response"""
    id: int

    class Config:
        from_attributes = True


class BookHATEOAS(BookResponse):
    """Book response with HATEOAS links"""
    links: List[Link] = []

    @staticmethod
    def from_book(book: "Book", base_url: str) -> "BookHATEOAS":
        """Create HATEOAS response from a Book ORM object"""
        return BookHATEOAS(
            id=book.id,
            title=book.title,
            author=book.author,
            price=book.price,
            isbn=book.isbn,
            in_stock=book.in_stock,
            links=[
                Link(rel="self", href=f"{base_url}/{book.id}", method="GET"),
                Link(rel="update", href=f"{base_url}/{book.id}", method="PUT"),
                Link(rel="delete", href=f"{base_url}/{book.id}", method="DELETE"),
                Link(rel="collection", href=base_url, method="GET"),
            ]
        )