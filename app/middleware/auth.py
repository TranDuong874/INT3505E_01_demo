import requests
from functools import wraps
from flask import request, jsonify, g
from app.utils.logger import get_logger

logger = get_logger(__name__)

AUTH_SERVER_URL = "http://localhost:3001"


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
                    # Check specific permission
                    response = requests.post(
                        f"{AUTH_SERVER_URL}/auth/check-permission",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"permission": permission},
                        timeout=5
                    )
                else:
                    # Just verify token
                    response = requests.post(
                        f"{AUTH_SERVER_URL}/auth/verify",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5
                    )
                
                if response.status_code == 401:
                    logger.warning(
                        "Authentication failed: Invalid or expired token",
                        extra={
                            "method": request.method,
                            "path": request.path,
                            "ip": request.remote_addr
                        }
                    )
                    return jsonify({"error": "Invalid or expired token"}), 401
                
                data = response.json()
                
                # Check permission if required
                if permission and not data.get('allowed', False):
                    logger.warning(
                        "Authorization failed: Insufficient permissions",
                        extra={
                            "method": request.method,
                            "path": request.path,
                            "ip": request.remote_addr,
                            "user": data.get('user'),
                            "role": data.get('role'),
                            "required_permission": permission
                        }
                    )
                    return jsonify({
                        "error": "Forbidden",
                        "message": f"Permission '{permission}' required",
                        "your_role": data.get('role')
                    }), 403
                
                # Store user info in Flask's g object for use in route
                g.current_user = data.get('user', {})
                
                logger.info(
                    "Authentication successful",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "ip": request.remote_addr,
                        "user": data.get('user') if permission else data.get('user', {}).get('username'),
                        "permission": permission
                    }
                )
                
                return f(*args, **kwargs)
                
            except requests.exceptions.ConnectionError:
                logger.error(
                    "Auth server unavailable",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "auth_server": AUTH_SERVER_URL
                    }
                )
                return jsonify({"error": "Authentication service unavailable"}), 503
            except requests.exceptions.Timeout:
                logger.error("Auth server timeout")
                return jsonify({"error": "Authentication service timeout"}), 503
            except Exception as e:
                logger.error(f"Auth error: {str(e)}")
                return jsonify({"error": "Authentication error"}), 500
        
        return decorated_function
    return decorator
