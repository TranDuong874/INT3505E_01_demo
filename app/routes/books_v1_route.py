from flask import jsonify, request
from flask import Blueprint
from app.middleware.limiter import limiter
from app.database.connection import SessionLocal
from app.services import books_service
from app.models.books_model import (
    BookCreate, BookUpdate, BookHATEOAS, 
    PaginatedResponse, Link
)

books_bp = Blueprint('books', __name__, url_prefix='/v1/books')


def get_db():
    """Get database session"""
    return SessionLocal()


def get_base_url():
    """Get base URL for HATEOAS links"""
    return request.host_url.rstrip('/') + '/v1/books'

@books_bp.route('/', methods=['GET'])
@limiter.limit("1 per second")
def get_books():
    """List all books with pagination"""
    db = get_db()
    try:
        page = request.args.get('page', 0, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        books = books_service.get_books(db, page=page, per_page=per_page)
        base_url = get_base_url()
        
        books_hateoas = [BookHATEOAS.from_book(book, base_url) for book in books]
        
        collection_links = [
            Link(rel="self", href=f"{base_url}?page={page}&per_page={per_page}", method="GET"),
            Link(rel="create", href=base_url, method="POST"),
        ]
        
        if page > 0:
            collection_links.append(
                Link(rel="prev", href=f"{base_url}?page={page-1}&per_page={per_page}", method="GET")
            )
        if len(books) == per_page:
            collection_links.append(
                Link(rel="next", href=f"{base_url}?page={page+1}&per_page={per_page}", method="GET")
            )
        
        response = PaginatedResponse(
            data=books_hateoas,
            links=collection_links,
            page=page,
            per_page=per_page
        )
        
        return jsonify(response.model_dump()), 200
    finally:
        db.close()

@books_bp.route('/', methods=['POST'])
@limiter.limit("1 per second")
def create_book():
    """Create a new book"""
    db = get_db()
    try:
        data = request.get_json()
        book_data = BookCreate(**data)
        
        book = books_service.create_book(db, book_data)
        base_url = get_base_url()
        
        response = BookHATEOAS.from_book(book, base_url)
        return jsonify(response.model_dump()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@books_bp.route('/<int:book_id>', methods=['GET'])
@limiter.limit("1 per second")
def get_book(book_id):
    """Get a book by ID"""
    db = get_db()
    try:
        book = books_service.get_book(db, book_id)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        base_url = get_base_url()
        response = BookHATEOAS.from_book(book, base_url)
        
        return jsonify(response.model_dump()), 200
    finally:
        db.close()

@books_bp.route('/<int:book_id>', methods=['PUT'])
@limiter.limit("1 per second")
def update_book(book_id):
    """Update a book"""
    db = get_db()
    try:
        data = request.get_json()
        book_data = BookUpdate(**data)
        
        book = books_service.update_book(db, book_id, book_data)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        base_url = get_base_url()
        response = BookHATEOAS.from_book(book, base_url)
        
        return jsonify(response.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@books_bp.route('/<int:book_id>', methods=['DELETE'])
@limiter.limit("1 per second")
def delete_book(book_id):
    """Delete a book"""
    db = get_db()
    try:
        book = books_service.delete_book(db, book_id)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        base_url = get_base_url()
        return jsonify({
            "message": f"Book {book_id} deleted successfully",
            "links": [
                {"rel": "collection", "href": base_url, "method": "GET"},
                {"rel": "create", "href": base_url, "method": "POST"}
            ]
        }), 200
    finally:
        db.close()