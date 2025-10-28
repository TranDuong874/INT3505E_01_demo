# Library Management System with OAuth2 Authentication

A RESTful API for managing books, copies, and user borrowing records.
## Architecture

- **Flask API**: Main library management service (Port 5000)
- **Node.js Auth Service**: OAuth2 token issuer and proxy (Port 8080)
- **SQLite Database**: Local file-based database (`./database/library.db`)

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm

## Quick Start

### 1. Start the Auth Service

**Windows:**
```bash
run_auth_service.bat
```

**Linux/Mac:**
```bash
chmod +x run_auth_service.sh
./run_auth_service.sh
```

**Manual:**
```bash
cd auth_service
npm install
node auth_service.js
```

### 2. Start the Flask App

**Windows:**
```bash
run_flask_app.bat
```

**Linux/Mac:**
```bash
chmod +x run_flask_app.sh
./run_flask_app.sh
```

**Manual:**
```bash
cd app
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r ../requirements.txt
python main.py
```

## API Usage

### 1. Get Access Token

```bash
curl -X POST http://localhost:8080/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "demo-client",
    "client_secret": "demo-secret",
    "scope": "borrows:read borrows:write",
    "audience": "flask-api"
  }'
```

### 2. Use the API

**Via Auth Service Proxy (Recommended):**
```bash
# Get borrows
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8080/api/borrows/

# Create borrow
curl -X POST -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "copy_id": 1}' \
  http://localhost:8080/api/borrows/
```

**Direct Flask API Access:**
```bash
# Get borrows
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:5000/borrows/
```

