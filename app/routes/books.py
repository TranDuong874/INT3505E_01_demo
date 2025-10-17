from flask import jsonify, request, Blueprint, make_response
from database import Book, User, LocalSession, BookCopy
from sqlalchemy.orm import joinedload

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.get('/', methods=['POST'])
def add_book():
    data = request.get_json()
    isbn = data.get('isbn')
    book_name = data.get('book_name', 'unknown')
    author = data.get('author', 'unknown')

    if not isbn:
        return jsonify({"error": "ISBN is required"}), 400

    session = LocalSession()

    try:
        book = session.query(Book).filter_by(isbn=isbn).first()
        if book:
            return jsonify({
                "error": f"Book with ISBN {isbn} already exists",
                "_links": {
                    "self": f"/books/{isbn}",
                    "add_copies": f"/copies/{isbn}"
                }
            }), 409  # Conflict

        # Create new book
        book = Book(isbn=isbn, book_name=book_name, author=author)
        session.add(book)
        session.commit()

        return jsonify({
            "data": {
                "isbn": book.isbn,
                "book_name": book.book_name,
                "author": book.author,
                "type": "book"
            },
            "_links": {
                "self": f"/books/{isbn}",
                "add_copies": f"books/{isbn}/copies/"
            }
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@books_bp.get("/", methods=["GET"])
def get_all_books():
    session = LocalSession()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page

        # Get total count and paginated results
        total = session.query(Book).count()
        books = session.query(Book).options(joinedload(Book.copies))\
            .offset(offset).limit(per_page).all()

        result = {
            "data": [
                {
                    "isbn": book.isbn,
                    "book_name": book.book_name,
                    "author": book.author,
                    "total_copies": len(book.copies),
                    "available_copies": sum(not copy.is_borrowed for copy in book.copies)
                }
                for book in books
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }

        response = make_response(jsonify(result))
        return response, 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@books_bp.get("/search", methods=["GET"])
def search_books():
    session = LocalSession()
    try:
        
        # Search parameters
        query = request.args.get('q', '').strip()
        search_by = request.args.get('by', 'all')  # all, name, author, isbn
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page
        
        # Base query with joins
        base_query = session.query(Book).options(joinedload(Book.copies))
        
        if query:
            if search_by == 'name':
                base_query = base_query.filter(Book.book_name.ilike(f'%{query}%'))
            elif search_by == 'author':
                base_query = base_query.filter(Book.author.ilike(f'%{query}%'))
            elif search_by == 'isbn':
                base_query = base_query.filter(Book.isbn.ilike(f'%{query}%'))
            else:  # search all fields
                base_query = base_query.filter(
                    (Book.book_name.ilike(f'%{query}%')) |
                    (Book.author.ilike(f'%{query}%')) |
                    (Book.isbn.ilike(f'%{query}%'))
                )
        
        total = base_query.count()
        books = base_query.offset(offset).limit(per_page).all()
        
        result = {
            "data": [
                {
                    "id": book.id,
                    "isbn": getattr(book, "isbn", None),
                    "book_name": book.book_name,
                    "author": getattr(book, "author", None),
                    "total_copies": len(book.copies),
                    "available_copies": sum(not copy.is_borrowed for copy in book.copies)
                }
                for book in books
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            },
            "search": {
                "query": query,
                "search_by": search_by
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
