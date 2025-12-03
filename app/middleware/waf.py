"""
Simple WAF - Logs suspicious requests for demo purposes.
Rate limiting handles DDoS protection.
"""
import re
from flask import request
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Simple patterns to detect (for logging only)
SUSPICIOUS_PATTERNS = [
    (r"(\%27)|(\')|(\-\-)", "SQL_INJECTION"),
    (r"<script", "XSS"),
    (r"\.\./", "PATH_TRAVERSAL"),
]


def setup_waf(app):
    """Setup simple WAF that only logs suspicious requests"""
    
    @app.before_request
    def log_suspicious_requests():
        # Check query parameters and path
        full_url = request.url
        
        for pattern, attack_type in SUSPICIOUS_PATTERNS:
            if re.search(pattern, full_url, re.IGNORECASE):
                logger.warning(
                    f"Suspicious request detected: {attack_type}",
                    extra={
                        "event_type": "WAF_ALERT",
                        "attack_type": attack_type,
                        "method": request.method,
                        "path": request.path,
                        "query": request.query_string.decode()[:200],
                        "ip": request.remote_addr,
                        "user_agent": request.headers.get('User-Agent', '')[:100]
                    }
                )
                # Don't block, just log for demo
                break

