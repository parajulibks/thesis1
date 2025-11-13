from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///asset_sentinel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

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

# Create and register models
import models as models_module
User, Asset, Alert, Setting = models_module.create_models(db, bcrypt)

# Make models available globally in app module
globals()['User'] = User
globals()['Asset'] = Asset
globals()['Alert'] = Alert
globals()['Setting'] = Setting

# Import and register blueprints
from routes import auth, users, assets, alerts, reports, settings

app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(users.bp, url_prefix='/api/users')
app.register_blueprint(assets.bp, url_prefix='/api/assets')
app.register_blueprint(alerts.bp, url_prefix='/api/alerts')
app.register_blueprint(reports.bp, url_prefix='/api/reports')
app.register_blueprint(settings.bp, url_prefix='/api/settings')

# Initialize database and create default admin user
def init_db():
    with app.app_context():
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
    init_db()
    
    # Start background scanner (disabled for now - can be enabled in production)
    # from scanner import start_background_scanner
    # start_background_scanner(app)
    
    print("Starting Asset Sentinel API server on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
