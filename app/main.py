from flask import Flask, send_file, render_template, Response
from flask_cors import CORS
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.database.connection import init_db
from app.routes.books_v1_route import books_bp
from app.utils.logger import setup_logging
from app.middleware.logger import setup_request_logging
from app.middleware.limiter import limiter
import os

logger = setup_logging(app_name="books-api")

app = Flask(__name__, template_folder='templates')

# Setup request/response logging (must be before limiter to catch rate limit errors)
setup_request_logging(app)

limiter.init_app(app)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(books_bp)

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


@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)

