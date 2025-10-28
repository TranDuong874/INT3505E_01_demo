from flask import Blueprint, request, jsonify
from database import LocalSession, Borrow, BookCopy, Book, User

import datetime

borrows_bp = Blueprint('borrows', __name__, url_prefix='/borrows')
@borrows_bp.route('/', methods=['POST'])
def borrow_book():
    data = request.get_json()
    user_id = data.get('user_id')
    copy_id = data.get('copy_id')

    if user_id is None:
        return jsonify({"error": "user_id not provided"}), 400
    if copy_id is None:
        return jsonify({"error": "copy_id not provided"}), 400

    start_date = datetime.date.today()
    session = LocalSession()
    try:
        book_copy = session.query(BookCopy).filter_by(id=copy_id).first()
        if not book_copy:
            return jsonify({"error": "Book copy not found"}), 404
        if book_copy.is_borrowed:
            return jsonify({"error": "Book copy already borrowed"}), 400

        new_borrow = Borrow(
            user_id=user_id,
            isbn=book_copy.isbn,
            copy_id=copy_id,
            start_date=start_date,
            end_date=None
        )
        session.add(new_borrow)
        book_copy.is_borrowed = True
        session.commit()
        session.refresh(new_borrow)

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
            }
        }
        return jsonify(response), 201, {'Location': f"/borrows/{new_borrow.id}"}
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@borrows_bp.route('/<borrow_id>', methods=['PATCH'])
def return_book(borrow_id):
    session = LocalSession()
    try:
        borrow_record = session.query(Borrow).filter_by(id=borrow_id).first()
        if not borrow_record:
            return jsonify({"error": "Borrow record not found"}), 404
            
        if borrow_record.end_date:
            return jsonify({"error": "Book already returned"}), 400

        book_copy = session.query(BookCopy).filter_by(id=borrow_record.copy_id).first()
        if not book_copy:
            return jsonify({"error": "Book copy not found"}), 404

        book_copy.is_borrowed = False
        borrow_record.end_date = datetime.date.today()
        session.commit()

        response = {
            "data": {
                "id": borrow_record.id,
                "user_id": borrow_record.user_id,
                "copy_id": borrow_record.copy_id,
                "start_date": borrow_record.start_date.isoformat(),
                "end_date": borrow_record.end_date.isoformat(),
                "borrowed_length": (borrow_record.end_date - borrow_record.start_date).days,
                "type": "borrow"
            },
            "_links": {
                "self": f"/borrows/{borrow_record.id}",
                "user": f"/users/{borrow_record.user_id}",
            }
        }
        return jsonify(response), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@borrows_bp.route('/', methods=['GET'])
def get_all_borrows():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    session = LocalSession()
    try:
        total = session.query(Borrow).count()
        borrows = session.query(Borrow).offset(offset).limit(per_page).all()
        total_pages = (total + per_page - 1) // per_page
        next_page = page + 1 if page < total_pages else total_pages
        prev_page = page - 1 if page > 1 else 1

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
                "pages": total_pages
            },
            "_links": {
                "self": {"href": f"/borrows?page={page}&per_page={per_page}"},
                "first": {"href": f"/borrows?page=1&per_page={per_page}"},
                "prev": {"href": f"/borrows?page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/borrows?page={next_page}&per_page={per_page}"},
                "last": {"href": f"/borrows?page={total_pages}&per_page={per_page}"}
            }
        }
        return jsonify(result), 200
    finally:
        session.close()
