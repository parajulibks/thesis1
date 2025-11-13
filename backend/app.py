from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize extensions (without app)
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///asset_sentinel.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Import routes
    from routes import auth, users, assets, alerts, reports, settings

    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(assets.bp, url_prefix='/api/assets')
    app.register_blueprint(alerts.bp, url_prefix='/api/alerts')
    app.register_blueprint(reports.bp, url_prefix='/api/reports')
    app.register_blueprint(settings.bp, url_prefix='/api/settings')

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({'error': 'Missing Authorization Header'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Asset Sentinel API',
            'version': '1.0.0',
            'status': 'running'
        })
    
    return app

# Initialize database and create default admin user
def init_db(app):
    with app.app_context():
        # Import models here
        from models import User, Asset, Alert, Setting
        
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@assetsentinel.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create default settings
            setting = Setting(
                key='scan_interval',
                value='2'
            )
            db.session.add(setting)
            
            setting2 = Setting(
                key='nvd_enabled',
                value='true'
            )
            db.session.add(setting2)
            
            setting3 = Setting(
                key='cisa_enabled',
                value='true'
            )
            db.session.add(setting3)
            
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")

if __name__ == '__main__':
    app = create_app()
    init_db(app)
    
    # Start background scanner
    from scanner import start_background_scanner
    start_background_scanner(app)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
