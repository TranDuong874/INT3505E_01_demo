from flask import Blueprint, request, jsonify
from database import LocalSession, Book, BookCopy
from sqlalchemy.orm import joinedload

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/', methods=['POST'])
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
                    "add_copies": f"/books/{isbn}/copies"
                }
            }), 409

        book = Book(isbn=isbn, book_name=book_name, author=author)
        session.add(book)
        session.commit()
        session.refresh(book)

        response = {
            "data": {
                "isbn": book.isbn,
                "book_name": book.book_name,
                "author": book.author,
                "type": "book"
            },
            "_links": {
                "self": f"/books/{isbn}",
                "copies": f"/books/{isbn}/copies"
            }
        }
        return jsonify(response), 201, {'Location': f"/books/{isbn}"}
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@books_bp.route("/", methods=["GET"])
def get_all_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()
    try:
        total = session.query(Book).count()
        books = session.query(Book).options(joinedload(Book.copies))\
            .offset(offset).limit(per_page).all()
        total_pages = (total + per_page - 1) // per_page
        next_page = page + 1 if page < total_pages else total_pages
        prev_page = page - 1 if page > 1 else 1

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
                "pages": total_pages
            },
            "_links": {
                "self": {"href": f"/books?page={page}&per_page={per_page}"},
                "first": {"href": f"/books?page=1&per_page={per_page}"},
                "prev": {"href": f"/books?page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/books?page={next_page}&per_page={per_page}"},
                "last": {"href": f"/books?page={total_pages}&per_page={per_page}"}
            }
        }
        return jsonify(result), 200
    finally:
        session.close()

@books_bp.route("/search", methods=["GET"])
def search_books():
    query = request.args.get('q', '').strip()
    search_by = request.args.get('by', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()
    try:
        base_query = session.query(Book).options(joinedload(Book.copies))
        
        if query:
            if search_by == 'name':
                base_query = base_query.filter(Book.book_name.ilike(f'%{query}%'))
            elif search_by == 'author':
                base_query = base_query.filter(Book.author.ilike(f'%{query}%'))
            elif search_by == 'isbn':
                base_query = base_query.filter(Book.isbn.ilike(f'%{query}%'))
            else:
                base_query = base_query.filter(
                    (Book.book_name.ilike(f'%{query}%')) |
                    (Book.author.ilike(f'%{query}%')) |
                    (Book.isbn.ilike(f'%{query}%'))
                )
        
        total = base_query.count()
        books = base_query.offset(offset).limit(per_page).all()
        total_pages = (total + per_page - 1) // per_page
        next_page = page + 1 if page < total_pages else total_pages
        prev_page = page - 1 if page > 1 else 1

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
                "pages": total_pages
            },
            "search": {
                "query": query,
                "search_by": search_by
            },
            "_links": {
                "self": {"href": f"/books/search?q={query}&by={search_by}&page={page}&per_page={per_page}"},
                "first": {"href": f"/books/search?q={query}&by={search_by}&page=1&per_page={per_page}"},
                "prev": {"href": f"/books/search?q={query}&by={search_by}&page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/books/search?q={query}&by={search_by}&page={next_page}&per_page={per_page}"},
                "last": {"href": f"/books/search?q={query}&by={search_by}&page={total_pages}&per_page={per_page}"}
            }
        }
        
        return jsonify(result), 200
    finally:
        session.close()
