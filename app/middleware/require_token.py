from flask import request, jsonify
from functools import wraps

API_TOKEN = 'example-token-key'

def require_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'error' : 'Unauthorized',
                'message' : 'Authorization header missing or empty'
            }), 401 

        try:
            scheme, token = auth_header.split()
        except ValueError:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authorization header format must be "Bearer [token]".'
            }), 401

        if scheme.lower() != 'bearer':
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authorization scheme must be "Bearer".'
            }), 401

        # 5. Validate the extracted token
        if token != API_TOKEN:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Invalid API token.'
            }), 403 # Using 403 Forbidden since we know the header exists but the credential is bad

        return func(*args, **kwargs)
        
    return wrapper
