import jwt
from flask import request, jsonify
from functools import wraps

AUTH_ISSUER = 'http://localhost:3000'
AUTH_AUDIENCE = 'flask-api'
SHARED_SECRET = 'demo-secret-key'


def get_token_claims():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, {"error": "missing_or_invalid_token"}
    
    token = auth_header.split(' ', 1)[1]
    try:
        claims = jwt.decode(
            token,
            SHARED_SECRET,
            algorithms=["HS256"],
            audience=AUTH_AUDIENCE,
            issuer=AUTH_ISSUER,
        )
        return claims, None
    except Exception as exc:
        return None, {"error": "invalid_token", "details": str(exc)}


def require_scope(required_scope: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims, error = get_token_claims()
            if error:
                return jsonify(error), 401

            token_scopes = set((claims.get('scope') or '').split())
            if required_scope not in token_scopes:
                return jsonify({"error": "insufficient_scope", "required": required_scope}), 403

            # Attach claims to request for use in route
            request.token_claims = claims
            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims, error = get_token_claims()
            if error:
                return jsonify(error), 401

            roles = claims.get('roles', [])
            if required_role not in roles:
                return jsonify({"error": "insufficient_permissions", "required_role": required_role}), 403

            # Attach claims to request for use in route
            request.token_claims = claims
            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_auth():
    """Decorator to just require valid authentication."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims, error = get_token_claims()
            if error:
                return jsonify(error), 401

            # Attach claims to request for use in route
            request.token_claims = claims
            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_any_scope(*required_scopes):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims, error = get_token_claims()
            if error:
                return jsonify(error), 401

            token_scopes = set((claims.get('scope') or '').split())
            if not any(scope in token_scopes for scope in required_scopes):
                return jsonify({
                    "error": "insufficient_scope",
                    "required_any": list(required_scopes)
                }), 403

            request.token_claims = claims
            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_all_scopes(*required_scopes):
    """Decorator to require all of the specified scopes."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims, error = get_token_claims()
            if error:
                return jsonify(error), 401

            token_scopes = set((claims.get('scope') or '').split())
            missing_scopes = [s for s in required_scopes if s not in token_scopes]
            if missing_scopes:
                return jsonify({
                    "error": "insufficient_scope",
                    "missing": missing_scopes
                }), 403

            request.token_claims = claims
            return func(*args, **kwargs)

        return wrapper
    return decorator