from flask import Flask, request, jsonify, make_response, send_from_directory, render_template
from markupsafe import escape
from database import Base, engine, User, LocalSession, Book, BookCopy, Borrow
import json
import datetime
from routes.books import books_bp
from routes.users.users_v1 import users_bp_v1
from routes.users.users_v2 import users_bp_v2
from routes.borrows import borrows_bp
from routes.copies import copies_bp
Base.metadata.create_all(bind=engine)

from functools import wraps

app = Flask(__name__)

app.register_blueprint(users_bp_v1)
app.register_blueprint(users_bp_v2)
app.register_blueprint(books_bp)
app.register_blueprint(borrows_bp)
app.register_blueprint(copies_bp)

@app.after_request
def add_header(response):
    # Add cache headers
    if request.method == 'GET':
        response.cache_control.public = True
        response.cache_control.max_age = 300 
        response.cache_control.must_revalidate = True
    else:
        response.cache_control.no_store = True 
    return response

@app.route("/openapi.yaml")
def serve_openapi():
    return send_from_directory(".", "docs/openapi.yaml")

@app.route("/swagger_docs")
def swagger_ui():
    return render_template("swagger.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    