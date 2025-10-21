# users_common.py
from flask import jsonify, request
from database import LocalSession, User, Borrow, BookCopy, Book

def get_user_info_by_id(user_id):
    session = LocalSession()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        borrows = session.query(Borrow).filter_by(user_id=user_id).all()
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
            "_links": {
                'self': f'/users/{user_id}',
                'borrows': f'/users/{user_id}/borrows'
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_user_borrows(user_id, page, per_page):
    session = LocalSession()
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
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
