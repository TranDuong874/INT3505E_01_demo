from flask import request, jsonify, Blueprint
from database import LocalSession, User, Book, BookCopy, Borrow

users_bp = Blueprint("users", __name__, url_prefix='/users')

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username")
    
    if not username:
        return jsonify({'error': 'Username not provided', 'status': 400}), 400

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
        return jsonify(response), 201, {'Location': f"/users/{new_user.id}"}
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@users_bp.route('/', methods=['GET'])
def get_all_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()

    try:
        total = session.query(User).count()
        users = session.query(User).offset(offset).limit(per_page).all()
        
        total_pages = (total + per_page - 1) // per_page
        next_page = page + 1 if page < total_pages else total_pages
        prev_page = page - 1 if page > 1 else 1

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
                "pages": total_pages
            }, 
            "_links": {
                "self": {"href": f"/users?page={page}&per_page={per_page}"},
                "first": {"href": f"/users?page=1&per_page={per_page}"},
                "prev": {"href": f"/users?page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/users?page={next_page}&per_page={per_page}"},
                "last": {"href": f"/users?page={total_pages}&per_page={per_page}"}
            }
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@users_bp.route("/user_id>", methods=["GET"])
def get_user_info_by_id(user_id):
    session = LocalSession()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        borrows = session.query(Borrow).filter_by(user_id=user_id).all()

        books_info = []
        for borrow in borrows:
            copy = session.query(BookCopy).filter_by(id=borrow.copy_id).first()
            if not copy:
                continue 
            
            book = session.query(Book).filter_by(isbn=copy.isbn).first()
            if not book:
                continue 

        return jsonify({
            'data': {
                "user_id": user.id,
                "username": user.username,
            },
            "_links" : {
                'self' : f'/users/{user_id}',
                'borrows' : f'users/{user_id}/borrows'
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@users_bp.route("/<user_id>/borrows", methods=['GET'])
def get_user_borrows(user_id):
    session = LocalSession()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404
        
        total = session.query(Borrow).filter_by(user_id=user_id).count()
        borrows = session.query(Borrow).filter_by(user_id=user_id).offset(offset).limit(per_page).all()

        total_pages = (total + per_page - 1) // per_page
        next_page = page + 1 if page < total_pages else total_pages
        prev_page = page - 1 if page > 1 else 1

        borrow_data = []
        for borrow in borrows:
            copy = session.query(BookCopy).filter_by(id=borrow.copy_id).first()
            book = session.query(Book).filter_by(isbn=borrow.isbn).first() if copy else None
            
            borrow_data.append({
                "borrow_id": borrow.id,
                "copy_id": borrow.copy_id,
                "isbn": borrow.isbn,
                "book_name": book.book_name if book else None,
                "start_date": borrow.start_date.isoformat() if borrow.start_date else None,
                "end_date": borrow.end_date.isoformat() if borrow.end_date else None
            })

        result = {
            'data': borrow_data,
            'pagination': {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": total_pages
            },
            "_links": {
                "self": {"href": f"/users/{user_id}/borrows?page={page}&per_page={per_page}"},
                "first": {"href": f"/users/{user_id}/borrows?page=1&per_page={per_page}"},
                "prev": {"href": f"/users/{user_id}/borrows?page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/users/{user_id}/borrows?page={next_page}&per_page={per_page}"},
                "last": {"href": f"/users/{user_id}/borrows?page={total_pages}&per_page={per_page}"}
            }
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()