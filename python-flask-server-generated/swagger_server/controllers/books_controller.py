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
from swagger_server.service.utils import normalize_pagination

from swagger_server.middleware.require_auth import require_auth

_CACHE = {}
_CACHE_ENABLED = False  

def _cache_key_list(page, per_page):
    return f"list:page={page}:per={per_page}"

def _cache_key_book(isbn):
    return f"book:isbn={isbn}"


def _db_book_to_book(db_book):
    """Convert database Book model to API Book model"""
    return Book(
        isbn=db_book.isbn,
        book_name=db_book.book_name,
        author=db_book.author,
        links=None  # Can be set if needed
    )


def books_get(page=None, per_page=None):  # noqa: E501
    """List books with pagination

     # noqa: E501

    :param page: Page number for pagination
    :type page: int
    :param per_page: Number of items per page
    :type per_page: int

    :rtype: InlineResponse200
    """
    try:
        page, per_page = normalize_pagination(page, per_page)

        # quick cache check
        if _CACHE_ENABLED:
            key = _cache_key_list(page, per_page)
            if key in _CACHE:
                print(f"CACHE HIT {key}")
                return _CACHE[key]

        db = next(get_db())

        total_items = db.query(BookModel).count()
        offset = (page - 1) * per_page
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 0

        books = db.query(BookModel).options(
            joinedload(BookModel.copies)
        ).offset(offset).limit(per_page).all()

        items = [_db_book_to_book(book) for book in books]

        pagination = Pagination(
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_items=total_items
        )

        response = InlineResponse200(
            limit=per_page,
            total=total_items,
            items=items,
            links=None,
            pagination=pagination
        )

        if _CACHE_ENABLED:
            try:
                _CACHE[key] = (response, 200)
                print(f"CACHE SET {key}")
            except Exception:
                pass

        return response, 200
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        if 'db' in locals() and db is not None:
            try:
                db.close()
            except Exception:
                pass


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
        
        deleted_book_data = {
            "isbn": book.isbn,
            "title": book.book_name,
            "author": book.author,
        }

        db.delete(book)
        db.commit()
        # clear cache on mutation
        if _CACHE_ENABLED:
            try:
                _CACHE.clear()
                print("CACHE CLEARED (delete)")
            except Exception:
                pass

        return deleted_book_data, 200 # Change 'Book' to none to invoke fail test, error code 204 will discard output
    except Exception as e:
        db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        if 'db' in locals() and db is not None:
            try:
                db.close()
            except Exception:
                pass


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
