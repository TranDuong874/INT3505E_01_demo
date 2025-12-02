from flask import Flask, send_file, render_template
from flask_cors import CORS
from app.database.connection import init_db
from app.routes.books_v1_route import books_bp
from app.utils.logger import setup_logging
from app.middleware.logging_middleware import setup_request_logging
import os

# Setup logging first
logger = setup_logging(app_name="books-api")

app = Flask(__name__, template_folder='templates')

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup request/response logging
setup_request_logging(app)

app.register_blueprint(books_bp)

# Initialize database
init_db()
logger.info("Application started", extra={"environment": "development"})


@app.route('/docs')
def docs():
    """Serve Swagger UI"""
    return render_template('swagger.html')


@app.route('/openapi.yaml')
def openapi_spec():
    """Serve OpenAPI YAML specification"""
    openapi_path = os.path.join(os.path.dirname(__file__), 'openapi.yaml')
    return send_file(openapi_path, mimetype='text/yaml')


if __name__ == "__main__":
    app.run(debug=True, port=5000)

