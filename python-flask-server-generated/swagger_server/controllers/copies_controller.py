import connexion
from sqlalchemy.orm import joinedload

from swagger_server.models.copies_copy_id_body import CopiesCopyIdBody  # noqa: E501
from swagger_server.models.copy import Copy  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.isbn_copies_body import IsbnCopiesBody  # noqa: E501
from swagger_server import util
from swagger_server.database import get_db, Book as BookModel, BookCopy
from swagger_server.controllers.authorization_controller import check_application

from swagger_server.middleware.require_auth import require_auth

def _status_to_is_borrowed(status):
    """Convert status string to is_borrowed boolean"""
    if status is None:
        return False
    status_lower = status.lower()
    # Consider "borrowed", "checked out", "unavailable" as borrowed
    return status_lower in ["borrowed", "checked out", "checked-out", "unavailable"]


def _is_borrowed_to_status(is_borrowed):
    return "borrowed" if is_borrowed else "available"


def _db_copy_to_copy(db_copy):
    """Convert database BookCopy model to API Copy model"""
    return Copy(
        copy_id=str(db_copy.id),
        status=_is_borrowed_to_status(db_copy.is_borrowed),
        links=None  # Can be set if needed
    )


def books_isbn_copies_copy_id_delete(isbn, copy_id):  # noqa: E501
    """Delete a copy by copy ID for a book

     # noqa: E501

    :param isbn: 
    :type isbn: str
    :param copy_id: 
    :type copy_id: str

    :rtype: None
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
        
        try:
            copy_id_int = int(copy_id)
        except ValueError:
            return Error(code=400, message="Invalid copy_id"), 400
        
        copy = db.query(BookCopy).filter(
            BookCopy.id == copy_id_int,
            BookCopy.isbn == isbn
        ).first()
        
        if not copy:
            return Error(code=404, message="Copy not found"), 404
        
        db.delete(copy)
        db.commit()
        
        return None, 204
    except Exception as e:
        db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_copies_copy_id_get(isbn, copy_id):  # noqa: E501
    """Get a copy by copy ID for a book

     # noqa: E501

    :param isbn: 
    :type isbn: str
    :param copy_id: 
    :type copy_id: str

    :rtype: Copy
    """
    try:
        db = next(get_db())
        
        book = db.query(BookModel).options(
            joinedload(BookModel.copies)
        ).filter(BookModel.isbn == isbn).first()
        
        if not book:
            return Error(code=404, message="Book not found"), 404
        
        try:
            copy_id_int = int(copy_id)
        except ValueError:
            return Error(code=400, message="Invalid copy_id"), 400
        
        copy = db.query(BookCopy).options(
            joinedload(BookCopy.book)
        ).filter(
            BookCopy.id == copy_id_int,
            BookCopy.isbn == isbn
        ).first()
        
        if not copy:
            return Error(code=404, message="Copy not found"), 404
        
        return _db_copy_to_copy(copy), 200
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_copies_copy_id_put(body, isbn, copy_id):  # noqa: E501
    """Update a copy by copy ID for a book

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param isbn: 
    :type isbn: str
    :param copy_id: 
    :type copy_id: str

    :rtype: Copy
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
        
        try:
            copy_id_int = int(copy_id)
        except ValueError:
            return Error(code=400, message="Invalid copy_id"), 400
        
        copy = db.query(BookCopy).filter(
            BookCopy.id == copy_id_int,
            BookCopy.isbn == isbn
        ).first()
        
        if not copy:
            return Error(code=404, message="Copy not found"), 404
        
        if connexion.request.is_json:
            body = CopiesCopyIdBody.from_dict(connexion.request.get_json())
        
        if body.status is not None:
            copy.is_borrowed = _status_to_is_borrowed(body.status)
        
        db.commit()
        db.refresh(copy)
        
        return _db_copy_to_copy(copy), 200
    except Exception as e:
        db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_copies_get(isbn):  # noqa: E501
    """List copies of a book by ISBN

     # noqa: E501

    :param isbn: 
    :type isbn: str

    :rtype: List[Copy]
    """
    try:
        db = next(get_db())
        
        book = db.query(BookModel).options(
            joinedload(BookModel.copies)
        ).filter(BookModel.isbn == isbn).first()
        
        if not book:
            return Error(code=404, message="Book not found"), 404
        
        copies = [_db_copy_to_copy(copy) for copy in book.copies]
        
        return copies, 200
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()


def books_isbn_copies_post(body, isbn):  # noqa: E501
    """Create a new copy for a book

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param isbn: 
    :type isbn: str

    :rtype: Copy
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
            body = IsbnCopiesBody.from_dict(connexion.request.get_json())
        
        is_borrowed = _status_to_is_borrowed(body.status) if body.status else False
        

        new_copy = BookCopy(
            isbn=isbn,
            is_borrowed=is_borrowed
        )
        
        
        db.add(new_copy)
        db.commit()
        db.refresh(new_copy)
        
        return _db_copy_to_copy(new_copy), 201
    except Exception as e:
        db.rollback()
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
    finally:
        db.close()
