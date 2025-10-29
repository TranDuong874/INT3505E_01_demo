import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from flask import request, jsonify
from functools import wraps

SECRET = "demo-secret-key"

def require_token(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.user = payload
        except ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)

    return decorator
