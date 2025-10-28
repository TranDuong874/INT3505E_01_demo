import jwt
from flask import request, jsonify
from functools import wraps

AUTH_ISSUER = 'http://localhost:8080'
AUTH_AUDIENCE = 'flask-api'
SHARED_SECRET = 'super-secret-dev-key'


def require_scope(required_scope: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "missing_or_invalid_token"}), 401
            token = auth_header.split(' ', 1)[1]
            try:
                claims = jwt.decode(
                    token,
                    SHARED_SECRET,
                    algorithms=["HS256"],
                    audience=AUTH_AUDIENCE,
                    issuer=AUTH_ISSUER,
                )
            except Exception as exc:
                return jsonify({"error": "invalid_token", "details": str(exc)}), 401

            token_scopes = set((claims.get('scope') or '').split())
            if required_scope not in token_scopes:
                return jsonify({"error": "insufficient_scope"}), 403

            return func(*args, **kwargs)

        return wrapper
    return decorator


