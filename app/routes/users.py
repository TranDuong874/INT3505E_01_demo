from flask import request, jsonify, Blueprint
from database import LocalSession, User, Book, BookCopy, Borrow

users_bp = Blueprint("users", __name__, url_prefix='/users')

@users_bp.route('/', methods=['POST'])
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
@users_bp.route('/', methods=['GET'])
def get_all_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()

    try:
        total = session.query(User).count()
        users = session.query(User).offset(offset).limit(per_page).all()
        
        next_page = min(page + 1, total)
        prev_page = max(page - 1, 0)
        first_page = 0
        last_page = total - 1

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
            }, 
            "_links" : {
                "self": { f"href": "/users?page={page}&per_page={per_page}" },
                "first": { f"href": "/users?page={first_page}&per_page={per_page}" },
                "prev": { f"href": "/users?page={prev_page}&per_page={per_page}" },
                "next": { f"href": "/users?page={next_page}&per_page={per_page}" },
                "last": { f"href": "/users?page={last_page}&per_page={per_page}" }
            }
        }
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error' : str(e)
        }), 404
    finally:
        session.close()


@users_bp.route("/<user_id>", methods=["GET"])
def get_user_info_by_id(user_id):
    session = LocalSession()
    try:
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
            'data': {
                "user_id": user.id,
                "username": user.username,
                "borrowed_books": books_info,
            }
        }), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@users_bp.route("/<user_id>/borrows", methods=['GET'])
def get_user_borrows(user_id):
    session = LocalSession()

    page = request.get('page')
    per_page = request.get('per_page')
    offset = int(page - 1) * per_page

    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({
                "error": f"User with ID {user_id} not found."
            }), 404
        
        total = session.query(Borrow).filter_by(user_id=user_id).count()
        borrows = session.query(Borrow).filter_by(user_id=user_id).\
                    offset(offset).\
                    limit(per_page).all()

        results = {
            'data' : [

            ],
            'pagination' : {

            }
        }

        return jsonify(results), 200
    except Exception as e:
        pass
    finally:
        session.close()
