from flask import Flask
from flask import request, jsonify
from markupsafe import escape
from .database import Base, engine, User, LocalSession
import json

Base.metadata.create_all(bind=engine)

app = Flask(__name__)

def get_db():
    db = LocalSession()
    try: 
        yield db
    finally:
        db.close()

# ==== User Actions ====
# Add user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username")
    
    if not username:
        return json({
            'error' : 'Username not provided',
        }, 400)

    session = LocalSession()

    try:
        new_user = User(username = username)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return jsonify({
            "id" : new_user.id, 
            "username" : new_user.username
        }, 201)
    except Exception as e:
        session.rollback()
        return jsonify({
            'error' : str(e)
        }, 400)
    
    finally:
        session.close()
        
# Get all users

# Get user renting information by name

# Get all books and available copies (count)

# Create a borrow (Rent book)

# Return book

# Add book


