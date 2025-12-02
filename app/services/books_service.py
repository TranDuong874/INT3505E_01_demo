from app.database.connection import get_db
from app.models.books_model import Book, BookCreate, BookUpdate
from app.utils.logger import get_logger
from app.utils.metrics import (
    books_created_total,
    books_deleted_total,
    books_count,
    db_errors_total,
    db_query_duration
)
import time

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

    start_time = time.time()
    try:
        db.add(book_db)
        db.commit()
        db.refresh(book_db)
        
        # Record metrics
        db_query_duration.labels(operation='create').observe(time.time() - start_time)
        books_created_total.inc()
        books_count.inc()
        
        logger.info("Book created successfully", extra={"book_id": book_db.id, "title": book_db.title})
        return book_db
    except Exception as e:
        db.rollback()
        db_errors_total.labels(operation='create').inc()
        logger.error("Failed to create book", extra={"error": str(e), "title": book_data.title}, exc_info=True)
        raise e
    
def get_book(db, book_id: int):
    """Retrieve a book by its ID."""
    logger.debug("Fetching book", extra={"book_id": book_id})
    
    start_time = time.time()
    try:
        book_db = db.query(Book).filter(Book.id == book_id).first()
        db_query_duration.labels(operation='get').observe(time.time() - start_time)
        
        if book_db:
            logger.info("Book found", extra={"book_id": book_id})
        else:
            logger.warning("Book not found", extra={"book_id": book_id})
        return book_db
    except Exception as e:
        db_errors_total.labels(operation='get').inc()
        logger.error("Error fetching book", extra={"book_id": book_id, "error": str(e)}, exc_info=True)
        raise e
    
def get_books(db, page:int=0, per_page:int=100):
    """Retrieve multiple books with pagination."""
    logger.debug("Fetching books", extra={"page": page, "per_page": per_page})
    
    start_time = time.time()
    try:
        books = db.query(Book).offset(page * per_page).limit(per_page).all()
        db_query_duration.labels(operation='list').observe(time.time() - start_time)
        
        logger.info("Books retrieved", extra={"count": len(books), "page": page})
        return books
    except Exception as e:
        db_errors_total.labels(operation='list').inc()
        logger.error("Error fetching books", extra={"error": str(e)}, exc_info=True)
        raise e

def update_book(db, book_id: int, book_data: BookUpdate):
    """Update an existing book record."""
    logger.info("Updating book", extra={"book_id": book_id})
    
    start_time = time.time()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.warning("Book not found for update", extra={"book_id": book_id})
            return None
        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
        
        db_query_duration.labels(operation='update').observe(time.time() - start_time)
        
        logger.info("Book updated successfully", extra={"book_id": book_id})
        return book
    except Exception as e:
        db.rollback()
        db_errors_total.labels(operation='update').inc()
        logger.error("Failed to update book", extra={"book_id": book_id, "error": str(e)}, exc_info=True)
        raise e
        

def delete_book(db, book_id: int):
    """Delete a book record by its ID."""
    logger.info("Deleting book", extra={"book_id": book_id})
    
    start_time = time.time()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.warning("Book not found for deletion", extra={"book_id": book_id})
            return None
        db.delete(book)
        db.commit()
        
        db_query_duration.labels(operation='delete').observe(time.time() - start_time)
        books_deleted_total.inc()
        books_count.dec()
        
        logger.info("Book deleted successfully", extra={"book_id": book_id})
        return book
    except Exception as e:
        db.rollback()
        db_errors_total.labels(operation='delete').inc()
        logger.error("Failed to delete book", extra={"book_id": book_id, "error": str(e)}, exc_info=True)
        raise e
    