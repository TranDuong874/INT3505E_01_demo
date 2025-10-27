from flask import Blueprint, request, jsonify
from database import LocalSession, Book, BookCopy
from sqlalchemy.orm import joinedload

copies_bp = Blueprint('copies', __name__, url_prefix='/books')

@copies_bp.route('/<isbn>/copies/', methods=['POST'])
def add_book_copies(isbn):
    data = request.get_json()
    count = max(data.get('count', 1), 1)

    session = LocalSession()
    try:
        book = session.query(Book).filter_by(isbn=isbn).first()
        if not book:
            return jsonify({"error": f"Book with ISBN {isbn} not found"}), 404

        book_copies = []
        for _ in range(count):
            copy = BookCopy(isbn=book.isbn, is_borrowed=False)
            session.add(copy)
            book_copies.append(copy)

        session.commit()
        for copy in book_copies:
            session.refresh(copy)

        response = {
            "data": {
                "isbn": book.isbn,
                "book_name": book.book_name,
                "added_copies": [
                    {
                        "id": copy.id,
                        "is_borrowed": copy.is_borrowed
                    } for copy in book_copies
                ],
                "count": len(book_copies),
                "type": "book_copies"
            },
            "_links": {
                "self": f"/books/{isbn}",
                "copies": f"/books/{isbn}/copies"
            }
        }
        return jsonify(response), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@copies_bp.route('/<isbn>/copies', methods=['GET'])
def get_list_of_copies_by_book(isbn):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()
    try:
        book = session.query(Book).filter(Book.isbn == isbn).options(joinedload(Book.copies)).first()
        
        if book is None:
            return jsonify({
                "error": "Not Found",
                "message": f"Book with ISBN '{isbn}' was not found."
            }), 404

        all_copies = book.copies
        total_copies = len(all_copies)
        copies_list = all_copies[offset:offset + per_page]
        total_pages = (total_copies + per_page - 1) // per_page
        next_page = page + 1 if page < total_pages else total_pages
        prev_page = page - 1 if page > 1 else 1

        result = {
            "data": {
                "isbn": book.isbn,
                "book_name": book.book_name,
                "author": book.author,
                "copies": [
                    {
                        "id": copy.id,
                        "is_borrowed": copy.is_borrowed
                    } for copy in copies_list
                ]
            },
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_copies,
                "pages": total_pages
            },
            "_links": {
                "self": {"href": f"/books/{isbn}/copies?page={page}&per_page={per_page}"},
                "first": {"href": f"/books/{isbn}/copies?page=1&per_page={per_page}"},
                "prev": {"href": f"/books/{isbn}/copies?page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/books/{isbn}/copies?page={next_page}&per_page={per_page}"},
                "last": {"href": f"/books/{isbn}/copies?page={total_pages}&per_page={per_page}"}
            }
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()