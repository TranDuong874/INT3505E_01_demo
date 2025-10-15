from flask import Flask, request, jsonify, make_response
from markupsafe import escape
from database import Base, engine, User, LocalSession, Book, BookCopy, Borrow
import json
import datetime
from sqlalchemy.orm import joinedload

Base.metadata.create_all(bind=engine)

app = Flask(__name__)

@app.after_request
def add_header(response):
    # Add cache headers
    if request.method == 'GET':
        response.cache_control.public = True
        response.cache_control.max_age = 300 
        response.cache_control.must_revalidate = True
    else:
        response.cache_control.no_store = True 
    return response

# ==== User Actions ====
# Add user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username")
    
    if not username:
        return jsonify({
            'error': 'Username not provided',
            'status': 400
        }), 400

    session = LocalSession()

    try:
        new_user = User(username=username)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        response = {
            "data": {
                "id": new_user.id,
                "username": new_user.username,
                "type": "user"
            },
            "_links": {
                "self": f"/users/{new_user.id}",
                "borrows": f"/users/{new_user.id}/borrows"
            }
        }
        return jsonify(response), 201, {
            'Location': f"/users/{new_user.id}"
        }
    except Exception as e:
        session.rollback()
        return jsonify({
            'error' : str(e)
        }), 400
    
    finally:
        session.close()
        
# Get all users
@app.route('/users', methods=['GET'])
def get_all_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()

    try:
        total = session.query(User).count()
        users = session.query(User).offset(offset).limit(per_page).all()
        
        result = {
            "data": [
                {
                    'id': user.id,
                    'username': user.username
                }
                for user in users
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error' : str(e)
        }), 404
    finally:
        session.close()

# ==== Book actions ====
# Create a borrow (Rent book)
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    isbn = data.get('isbn')
    book_name = data.get('book_name', 'unknown')
    author = data.get('author', 'unknown')
    count = data.get('count', 1)
    count = max(count, 1)
    if not isbn:
        return jsonify({
            "error": "ISBN is required"}), 400

    session = LocalSession()

    try:
        book = session.query(Book).filter_by(isbn=isbn).first()
        warning = ""

        if book:
            if book.book_name != book_name:
                warning = f"WARNING: A book with ISBN {isbn} already exists. Using existing book name: {book.book_name}"
        else:
            book = Book(isbn=isbn, book_name=book_name, author=author)
            session.add(book)
            session.flush()  # assigns book.id without committing

        book_copies = []
        for _ in range(count):
            copy = BookCopy(isbn=book.isbn, is_borrowed=False)
            session.add(copy)
            book_copies.append(copy)

        session.commit()

        return jsonify({
            "message": f"{warning}\nAdded {max(count, 1)} copies for book {book.book_name}",
            "book": {"isbn": book.isbn, "book_name": book.book_name, "author": book.author},
            "added_copies": [{"id": cpy.id} for cpy in book_copies]
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({
            "error": str(e)
        }), 400

    finally:
        session.close()

@app.route('/borrows', methods=['POST'])
def borrow_book():
    data = request.get_json()
    user_id = data.get('user_id')
    copy_id = data.get('copy_id')

    if user_id is None:
        return jsonify({"error": "user_id not provided"}), 400
    if copy_id is None:
        return jsonify({"error": "copy_id not provided"}), 400

    start_date = datetime.date.today()

    try:
        session = LocalSession()

        book_copy = session.query(BookCopy).filter_by(id=copy_id).first()
        if not book_copy:
            return jsonify({
                "error": "Book copy not found"
            }), 404
        if book_copy.is_borrowed:
            return jsonify({
                "error": "Book copy already borrowed"
            }, 400)

        new_borrow = Borrow(
            user_id = user_id,
            isbn = book_copy.isbn,
            copy_id = copy_id,
            start_date=start_date,
            end_date=None
        )
        session.add(new_borrow)

        book_copy.is_borrowed = True

        session.commit()

        response = {
            "data": {
                "id": new_borrow.id,
                "user_id": user_id,
                "copy_id": copy_id,
                "start_date": start_date.isoformat(),
                "type": "borrow"
            },
            "_links": {
                "self": f"/borrows/{new_borrow.id}",
                "user": f"/users/{user_id}",
                "book_copy": f"/books/{book_copy.isbn}/copies/{copy_id}"
            }
        }
        return jsonify(response), 201, {
            'Location': f"/borrows/{new_borrow.id}"
        }

    except Exception as e:
        session.rollback()
        return jsonify({
            "error": str(e)
        }), 400
    finally:
        session.close()

# Return book
@app.route('/returns', methods=['POST'])
def return_book():
    data = request.get_json()
    user_id = data.get('user_id')
    copy_id = data.get('copy_id')

    if user_id is None:
        return jsonify({"error": "user_id not provided"}), 400
    if copy_id is None:
        return jsonify({"error": "copy_id not provided"}), 400


    try:
        session = LocalSession()

        book_copy = session.query(BookCopy).filter_by(id=copy_id).first()
        if not book_copy:
            return jsonify({
                "error": "Book copy not found"
            }), 404
        if not book_copy.is_borrowed:
            return jsonify({
                "error": "Book copy is not borrowed"
            }), 400

        book_copy.is_borrowed = False
            
        borrow_record = session.query(Borrow).filter_by(user_id=user_id, copy_id=copy_id).first()
        borrow_record.end_date = datetime.date.today()

        session.commit()

        return jsonify({
            "message": "Book returned successfully",
            "start_date" : borrow_record.start_date,
            "end_date" : borrow_record.end_date,
            "borrowed_length" : (borrow_record.end_date - borrow_record.start_date).days,
            "borrow_id": borrow_record.id
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({
            "error": str(e)
        }), 400
    finally:
        session.close()

@app.route("/books", methods=["GET"])
def get_all_books():
    try:
        session = LocalSession()
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
            }
        }

        response = make_response(jsonify(result))
        return response, 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

from flask import jsonify

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_info_by_id(user_id):
    try:
        session = LocalSession()

        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        borrow_records = session.query(Borrow).filter_by(user_id=user_id).all()

        books_info = []
        for record in borrow_records:
            copy = session.query(BookCopy).filter_by(id=record.copy_id).first()
            if not copy:
                continue 
            
            book = session.query(Book).filter_by(isbn=copy.isbn).first()
            if not book:
                continue 

            books_info.append({
                "copy_id": copy.id,
                "isbn": getattr(book, "isbn", None),
                "book_name": book.book_name,
                "author": getattr(book, "author", None),
                "is_borrowed": copy.is_borrowed,
                "start_date": record.start_date.isoformat() if record.start_date else None,
                "end_date": record.end_date.isoformat() if record.end_date else None
            })

        return jsonify({
            "user_id": user.id,
            "username": user.username,
            "borrowed_books": books_info
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@app.route('/borrows', methods=['GET'])
def get_all_borrows():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()

    try:
        total = session.query(Borrow).count()
        borrows = session.query(Borrow).offset(offset).limit(per_page).all()

        result = {
            "data": [
                {
                    "id": borrow.id,
                    "user_id": borrow.user_id,
                    "copy_id": borrow.copy_id,
                    "start_date": borrow.start_date.isoformat() if borrow.start_date else None,
                    "end_date": borrow.end_date.isoformat() if borrow.end_date else None
                }
                for borrow in borrows
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
