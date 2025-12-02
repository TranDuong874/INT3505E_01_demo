import time
from flask import request, g
from functools import wraps
from app.utils.logger import get_logger

logger = get_logger(__name__)


def log_request():
    """
    Middleware to log all HTTP requests and responses
    Records: method, path, status code, duration, IP address
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Start timer
            g.start_time = time.time()
            
            # Log incoming request
            logger.info(
                "Incoming request",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "ip": request.remote_addr,
                    "user_agent": request.user_agent.string
                }
            )
            
            # Execute the route handler
            try:
                response = f(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - g.start_time
                
                # Get status code
                if isinstance(response, tuple):
                    status_code = response[1] if len(response) > 1 else 200
                else:
                    status_code = 200
                
                # Log successful response
                logger.info(
                    "Request completed",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "status_code": status_code,
                        "duration_ms": round(duration * 1000, 2),
                        "ip": request.remote_addr
                    }
                )
                
                return response
                
            except Exception as e:
                # Calculate duration
                duration = time.time() - g.start_time
                
                # Log error
                logger.error(
                    "Request failed",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "ip": request.remote_addr
                    },
                    exc_info=True
                )
                raise
        
        return decorated_function
    return decorator


def setup_request_logging(app):
    """
    Setup Flask before/after request handlers for logging
    """
    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.path,
                "ip": request.remote_addr,
                "user_agent": request.user_agent.string
            }
        )
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "ip": request.remote_addr
                }
            )
        return response
    
    @app.errorhandler(404)
    def handle_not_found(e):
        logger.warning(
            "Resource not found",
            extra={
                "method": request.method,
                "path": request.path,
                "ip": request.remote_addr
            }
        )
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
        else:
            duration = 0
        
        logger.error(
            "Unhandled exception",
            extra={
                "method": request.method,
                "path": request.path,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(duration * 1000, 2),
                "ip": request.remote_addr
            },
            exc_info=True
        )
        
        return {"error": "Internal server error"}, 500
