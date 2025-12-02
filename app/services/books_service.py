from app.database.connection import get_db
from app.models.books_model import Book, BookCreate, BookUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_book(db, book_data: BookCreate):
    """Create a new book record in the database."""
    logger.info("Creating new book", extra={"title": book_data.title, "author": book_data.author})
    
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
        logger.info("Book created successfully", extra={"book_id": book_db.id, "title": book_db.title})
        return book_db
    except Exception as e:
        db.rollback()
        logger.error("Failed to create book", extra={"error": str(e), "title": book_data.title}, exc_info=True)
        raise e
    
def get_book(db, book_id: int):
    """Retrieve a book by its ID."""
    logger.debug("Fetching book", extra={"book_id": book_id})
    try:
        book_db = db.query(Book).filter(Book.id == book_id).first()
        if book_db:
            logger.info("Book found", extra={"book_id": book_id})
        else:
            logger.warning("Book not found", extra={"book_id": book_id})
        return book_db
    except Exception as e:
        logger.error("Error fetching book", extra={"book_id": book_id, "error": str(e)}, exc_info=True)
        raise e
    
def get_books(db, page:int=0, per_page:int=100):
    """Retrieve multiple books with pagination."""
    logger.debug("Fetching books", extra={"page": page, "per_page": per_page})
    try:
        books = db.query(Book).offset(page * per_page).limit(per_page).all()
        logger.info("Books retrieved", extra={"count": len(books), "page": page})
        return books
    except Exception as e:
        logger.error("Error fetching books", extra={"error": str(e)}, exc_info=True)
        raise e

def update_book(db, book_id: int, book_data: BookUpdate):
    """Update an existing book record."""
    logger.info("Updating book", extra={"book_id": book_id})
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.warning("Book not found for update", extra={"book_id": book_id})
            return None
        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
        logger.info("Book updated successfully", extra={"book_id": book_id})
        return book
    except Exception as e:
        db.rollback()
        logger.error("Failed to update book", extra={"book_id": book_id, "error": str(e)}, exc_info=True)
        raise e
        

def delete_book(db, book_id: int):
    """Delete a book record by its ID."""
    logger.info("Deleting book", extra={"book_id": book_id})
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.warning("Book not found for deletion", extra={"book_id": book_id})
            return None
        db.delete(book)
        db.commit()
        logger.info("Book deleted successfully", extra={"book_id": book_id})
        return book
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete book", extra={"book_id": book_id, "error": str(e)}, exc_info=True)
        raise e
    