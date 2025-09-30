from flask import Flask
from flask import request, jsonify
from markupsafe import escape
from .database import Base, engine, User, LocalSession, Book, BookCopy
import json

Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# ==== User Actions ====
# Add user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username")
    
    if not username:
        return json({
            'error' : 'Username not provided',
        }), 400

    session = LocalSession()

    try:
        new_user = User(username = username)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return jsonify({
            "id" : new_user.id, 
            "username" : new_user.username
        }), 201
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
    n_users = request.args.get('limit', default=10, type=int)
    session = LocalSession()

    try:
        users = session.query(User).limit(n_users).all()
        user_list = [
            {
                'id' : user.id,
                'user_name' : user.username
            }
            for user in users
        ]

        return jsonify(user_list), 200
    
    except Exception as e:
        return jsonify({
            'error' : str(e)
        }), 404
    finally:
        session.close()

# Get user renting information by name

# Get all books and available copies (count)

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

# Return book

# Add book
