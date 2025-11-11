import connexion

def require_auth():
    """Check if user is authenticated and has write permission"""
    try:
        token = connexion.request.headers.get('Authorization', '')
        if token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            return None
        
        user_info = check_application(token)
        if not user_info:
            return None
        
        scopes = user_info.get('scopes', [])
        if 'write:books' not in scopes and 'write' not in scopes:
            return None
        
        return user_info
    except Exception:
        return None