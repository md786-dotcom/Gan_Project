from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

# Load environment variables (optional - works without .env file)
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per minute", "2000 per hour"]  # More generous limits for GUI
)

def create_app():
    app = Flask(__name__)
    
    # Configuration - all with sensible defaults
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'image-processing-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # Database configuration with instance directory for SQLite
    db_url = os.getenv('DATABASE_URL', 'sqlite:///image_service.db')
    if db_url.startswith('sqlite:///') and not db_url.startswith('sqlite:////'):
        # Ensure SQLite database is in instance directory
        db_name = db_url.replace('sqlite:///', '')
        instance_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_dir, db_name)}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    csrf.init_app(app)
    CORS(app, origins=["http://localhost:5000"])  # Only allow same origin
    limiter.init_app(app)
    
    # Register API blueprints
    from app.routes.auth import auth_bp
    from app.routes.images import images_bp
    from app.routes.web import web_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(web_bp, url_prefix='/')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'OK', 'message': 'Image Processing Service is running'}
    
    # Error handlers for security
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad request'}), 400
        return render_template('error.html', error="Bad Request", message="Invalid request"), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('error.html', error="Forbidden", message="Access denied"), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('error.html', error="Not Found", message="Page not found"), 404
    
    @app.errorhandler(413)
    def file_too_large(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413
        return render_template('error.html', error="File Too Large", message="Maximum file size is 16MB"), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('error.html', error="Server Error", message="Something went wrong"), 500
    
    return app