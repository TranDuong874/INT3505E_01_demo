import requests
from functools import wraps
from flask import request, jsonify, g
from app.utils.logger import get_logger
from app.middleware import circuit_breaker

logger = get_logger(__name__)

AUTH_SERVER_URL = "http://localhost:3001"

auth_breaker = CircuitBreaker(failure_threshold=3. recovery_timeout=10)

def _call_auth_server(endpoint, token, json_data=None):
    """Call auth server"""
    @auth_breaker.call
    def call():
        return requests.post(
            f"{AUTH_SERVER_URL}{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            json=json_data,
            timeout=5
        )
    return call()
    

def require_auth(permission=None):
    """
    Decorator to require authentication and optionally check permission.
    
    Usage:
        @require_auth()  # Just verify token
        @require_auth('read')  # Verify token + check 'read' permission
        @require_auth('delete')  # Verify token + check 'delete' permission
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning(
                    "Authentication failed: No token provided",
                    extra={
                        "event_type": "AUTH_FAILURE",
                        "reason": "NO_TOKEN",
                        "method": request.method,
                        "path": request.path,
                        "ip": request.remote_addr
                    }
                )
                return jsonify({"error": "Authorization header required"}), 401
            
            token = auth_header.split(' ')[1]
            
            try:
                # Verify token with auth server
                if permission:
                    response = _call_auth_server(
                        "/auth/check-permission",
                        token,
                        {"permission": permission}
                    )
                else:
                    response = _call_auth_server("/auth/verify", token)
                
                if response.status_code == 401:
                    logger.warning(
                        "Authentication failed: Invalid or expired token",
                        extra={
                            "event_type": "AUTH_FAILURE",
                            "reason": "INVALID_TOKEN",
                            "method": request.method,
                            "path": request.path,
                            "ip": request.remote_addr
                        }
                    )
                    return jsonify({"error": "Invalid or expired token"}), 401
                
                data = response.json()
                user = data.get('user') if permission else data.get('user', {}).get('username')
                role = data.get('role') if permission else data.get('user', {}).get('role')
                
                # Check permission if required
                if permission and not data.get('allowed', False):
                    logger.warning(
                        "Authorization failed: Insufficient permissions",
                        extra={
                            "event_type": "AUTH_FORBIDDEN",
                            "reason": "INSUFFICIENT_PERMISSIONS",
                            "method": request.method,
                            "path": request.path,
                            "ip": request.remote_addr,
                            "user": user,
                            "role": role,
                            "required_permission": permission
                        }
                    )
                    return jsonify({
                        "error": "Forbidden",
                        "message": f"Permission '{permission}' required",
                        "your_role": role
                    }), 403
                
                # Store user info in Flask's g object for use in route
                g.current_user = data.get('user', {})
                
                logger.info(
                    "Authentication successful",
                    extra={
                        "event_type": "AUTH_SUCCESS",
                        "method": request.method,
                        "path": request.path,
                        "ip": request.remote_addr,
                        "user": user,
                        "role": role,
                        "permission": permission
                    }
                )
                
                return f(*args, **kwargs)
                
            except requests.exceptions.ConnectionError:
                logger.error(
                    "Auth server unavailable",
                    extra={
                        "event_type": "AUTH_SERVER_DOWN",
                        "method": request.method,
                        "path": request.path,
                        "auth_server": AUTH_SERVER_URL
                    }
                )
                return jsonify({"error": "Authentication service unavailable"}), 503
                
            except requests.exceptions.Timeout:
                logger.error(
                    "Auth server timeout",
                    extra={
                        "event_type": "AUTH_TIMEOUT",
                        "method": request.method,
                        "path": request.path
                    }
                )
                return jsonify({"error": "Authentication service timeout"}), 503
                
            except Exception as e:
                logger.error(
                    f"Auth error: {str(e)}",
                    extra={
                        "event_type": "AUTH_ERROR",
                        "error": str(e),
                        "method": request.method,
                        "path": request.path
                    }
                )
                return jsonify({"error": "Authentication error"}), 500
        
        return decorated_function
    return decorator
