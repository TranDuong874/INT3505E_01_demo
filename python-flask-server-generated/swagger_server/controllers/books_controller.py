import connexion
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.books_body import BooksBody  # noqa: E501
from swagger_server.models.books_isbn_body import BooksIsbnBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.pagination import Pagination  # noqa: E501
from swagger_server.models.hateoas_links import HateoasLinks  # noqa: E501
from swagger_server import util
from swagger_server.database import get_db, Book as BookModel
from swagger_server.controllers.authorization_controller import check_application

from swagger_server.middleware.require_auth import require_auth


def _db_book_to_book(db_book):
    """Convert database Book model to API Book model"""
    return Book(
        isbn=db_book.isbn,
        book_name=db_book.book_name,
        author=db_book.author,
        links=None  # Can be set if needed
    )


def books_get(offset=None, limit=None, page=None, per_page=None):  # noqa: E501
    """List books with pagination

     # noqa: E501

    :param offset: Offset for pagination (starting from 0)
    :type offset: int
    :param limit: Number of items per page
    :type limit: int
    :param page: Page number for pagination
    :type page: int
    :param per_page: Number of items per page
    :type per_page: int

    :rtype: InlineResponse200
    """
    try:
        db = next(get_db())
        
        page = max(1, page or 1)
        per_page = max(1, min(50, per_page or 10))  # default 10, max 50

        total_items = db.query(BookModel).count()
        offset = (page - 1) * per_page
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 0

        books = db.query(BookModel).options(
            joinedload(BookModel.copies)
        ).offset(offset).limit(limit).all()

        items = [_db_book_to_book(book) for book in books]
        
        pagination = Pagination(
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_items=total_items
        )
        
        response = InlineResponse200(
            offset=offset,
            limit=limit,
            total=total_items,
            items=items,
            links=None,
            pagination=pagination
        )
        
        return response, 200
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_delete(isbn):  # noqa: E501
    """Delete a book by ISBN

     # noqa: E501

    :param isbn: 
    :type isbn: str

    :rtype: None
    """
    # Require authentication
    # user_info = require_auth()
    # if not user_info:
    #     return Error(code=401, message="Unauthorized"), 401
    
    try:
        db = next(get_db())
        
        # Check if book exists
        book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
        if not book:
            return Error(code=404, message="Book not found"), 404
        
        # Delete the book (cascading will handle copies if configured)
        db.delete(book)
        db.commit()
        
        return None, 204
    except Exception as e:
        db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_get(isbn):  # noqa: E501
    """Get a book by ISBN

     # noqa: E501

    :param isbn: 
    :type isbn: str

    :rtype: Book
    """
    try:
        db = next(get_db())
        
        # Query book with joined loading of copies
        book = db.query(BookModel).options(
            joinedload(BookModel.copies)
        ).filter(BookModel.isbn == isbn).first()
        
        if not book:
            return Error(code=404, message="Book not found"), 404
        
        return _db_book_to_book(book), 200
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_put(body, isbn):  # noqa: E501
    """Update a book by ISBN

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param isbn: 
    :type isbn: str

    :rtype: Book
    """
    # Require authentication
    # user_info = require_auth()
    # if not user_info:
    #     return Error(code=401, message="Unauthorized"), 401
    
    try:
        db = next(get_db())
        
        book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
        if not book:
            return Error(code=404, message="Book not found"), 404
        
        if connexion.request.is_json:
            body = BooksIsbnBody.from_dict(connexion.request.get_json())
        
        if body.book_name is not None:
            book.book_name = body.book_name
        if body.author is not None:
            book.author = body.author
        
        db.commit()
        db.refresh(book)
        
        return _db_book_to_book(book), 200
    except Exception as e:
        db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_post(body):  # noqa: E501
    """Create a new book

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Book
    """
    # Require authentication
    # user_info = require_auth()
    # if not user_info:
    #     return Error(code=401, message="Unauthorized"), 401
    
    try:
        if connexion.request.is_json:
            body = BooksBody.from_dict(connexion.request.get_json())
        
        if not body.isbn or not body.book_name or not body.author:
            return Error(code=400, message="ISBN, book_name, and author are required"), 400
        
        db = next(get_db())
        
        existing_book = db.query(BookModel).filter(BookModel.isbn == body.isbn).first()
        if existing_book:
            return Error(code=409, message="Book with this ISBN already exists"), 409
        
        new_book = BookModel(
            isbn=body.isbn,
            book_name=body.book_name,
            author=body.author
        )
        
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        
        return _db_book_to_book(new_book), 201
    except IntegrityError:
        db.rollback()
        return Error(code=409, message="Book with this ISBN already exists"), 409
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        if 'db' in locals():
            db.close()
