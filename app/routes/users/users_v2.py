# users_v2.py
from flask import Blueprint, request, jsonify
from database import LocalSession, User
from .users_common import get_user_info_by_id, get_user_borrows
from middleware.auth import require_scope, require_auth, require_role

users_bp_v2 = Blueprint("users_v2", __name__, url_prefix="/api/v2/users")

@users_bp_v2.route("/", methods=["GET"])
@require_scope('users:read')
def get_all_users_v2():
    # new logic for v2 - include extra field
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
            "data": [{"id": u.id, "username": u.username, "extra_info": "v2"} for u in users],
            "pagination": {"page": page, "per_page": per_page, "total": total, "pages": total_pages},
            "_links": {
                "self": {"href": f"/users?page={page}&per_page={per_page}"},
                "first": {"href": f"/users?page=1&per_page={per_page}"},
                "prev": {"href": f"/users?page={prev_page}&per_page={per_page}"},
                "next": {"href": f"/users?page={next_page}&per_page={per_page}"},
                "last": {"href": f"/users?page={total_pages}&per_page={per_page}"}
            }
        }
        return jsonify(result), 200
    finally:
        session.close()

@users_bp_v2.route("/<user_id>", methods=["GET"])
@require_scope('users:read')
def get_user_by_id(user_id):
    return get_user_info_by_id(user_id)

@users_bp_v2.route("/<user_id>/borrows", methods=["GET"])
@require_scope('users:read')
def get_user_borrows(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    result, status = get_user_borrows(user_id, page, per_page)
    return jsonify(result), status
