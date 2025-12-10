TARGET_ENDPOINT='http://localhost:5001/webhook/notify' # Test endpoint

def notify(method, data=None):
    payload = {
        'event' : method,
        'data': data or {}
    }

    try:
        response = request.post(TARGET_ENDPOINT, json=payload, timeout=5)
        response.raise_for_status()
        return response.status_code
    except Exception as e:
        print(f"Webhook notification failed: {e}")
        return None