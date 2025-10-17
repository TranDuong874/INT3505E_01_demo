from flask import jsonify, request, Blueprint, make_response
from database import Book, User, LocalSession, BookCopy
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

        return jsonify({
            "data": {
                "isbn": book.isbn,
                "book_name": book.book_name,
                "added_copies": [
                    {
                        "id": copy.id,
                        "_links": {
                            "self": f"/copies/{copy.id}/",
                        },
                        "is_borrowed" : copy.is_borrowed
                    } for copy in book_copies
                ],
                "count": len(book_copies),
                "type": "book_copies"
            },
            "_links": {
                "book": f"/books/{isbn}",
            }
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@copies_bp.route('/<isbn>/copies', methods=['GET'])
def get_list_of_copies_by_book(isbn):
    session = LocalSession()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page

        book = session.query(Book).filter(Book.isbn == isbn).options(joinedload(Book.copies)).first()
        
        if book is None:
            return jsonify({
                "error": "Not Found",
                "message": f"Book with ISBN '{isbn}' was not found."
            }), 404
        else:
            # Manually paginate the fully loaded list of copies in Python
            all_copies = book.copies
            total_copies = len(all_copies)
            copies_list = all_copies[offset:offset + per_page]
            total_pages = (total_copies + per_page - 1) // per_page

            # Pagination links
            base_url = f"/books/{isbn}/copies"
            links = {
                "self": f"{base_url}?page={page}&per_page={per_page}",
                "first": f"{base_url}?page=1&per_page={per_page}",
                "last": f"{base_url}?page={total_pages}&per_page={per_page}"
            }

            if page < total_pages:
                links["next"] = f"{base_url}?page={page + 1}&per_page={per_page}"
            if page > 1:
                links["prev"] = f"{base_url}?page={page - 1}&per_page={per_page}"
            
            return jsonify({
                "data" : {
                    "book" : { 
                        'isbn' : book.isbn,
                        'title' : book.title,
                        "_links": {"self": f"/books/{book.isbn}"}
                    },
                    "copies_list" : [
                        {
                            "id" : copy.id,
                            "is_borrowed" : copy.is_borrowed,
                            "_links" : {
                                "copy" : f"/copies/{copy.id}"
                            }
                        } for copy in copies_list
                    ],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_items": total_copies,
                        "total_pages": total_pages
                    }
                },
                "_links": links 
            }), 200
        
    except Exception as e:
        return jsonify({'error' : str(e)}), 500 
    finally:
        session.close()