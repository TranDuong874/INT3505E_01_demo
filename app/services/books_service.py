from app.database.connection import get_db
from app.models.books_model import Book, BookCreate, BookUpdate

def  create_book(db, book_data: BookCreate):
    """Create a new book record in the database."""
    book_db = Book(
        title=book_data.title,
        author=book_data.author,
        price=book_data.price,
        isbn=book_data.isbn
    )    

    try:
        db.add(book_db)
        db.commit()
        db.refresh(book_db)
        return book_db
    except Exception as e:
        db.rollback()
        raise e
    
def get_book(db, book_id: int):
    """Retrieve a book by its ID."""
    try:
        book_db = db.query(Book).filter(Book.id == book_id).first()
        return book_db
    except Exception as e:
        raise e
    
def get_books(db, page:int=0, per_page:int=100):
    """Retrieve multiple books with pagination."""
    try:
        books = db.query(Book).offset(page * per_page).limit(per_page).all()
        return books
    except Exception as e:
        raise e

def update_book(db, book_id: int, book_data: BookUpdate):
    """Update an existing book record."""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None
        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
        return book
    except Exception as e:
        db.rollback()
        raise e
        

def delete_book(db, book_id: int):
    """Delete a book record by its ID."""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None
        db.delete(book)
        db.commit()
        return book
    except Exception as e:
        db.rollback()
        raise e
    