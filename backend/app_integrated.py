"""
Asset Sentinel - Integrated Backend and Frontend Server
This file serves both the API endpoints and the frontend static files
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta, datetime
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()

# Initialize Flask app with static folder pointing to frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='')

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

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    hostname = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))
    asset_type = db.Column(db.String(100))
    os = db.Column(db.String(200))
    firmware_version = db.Column(db.String(100))
    criticality = db.Column(db.String(20), default='medium')
    tags = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'asset_type': self.asset_type,
            'os': self.os,
            'firmware_version': self.firmware_version,
            'criticality': self.criticality,
            'tags': self.tags.split(',') if self.tags else [],
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    cve_id = db.Column(db.String(20))
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), nullable=False)
    cvss_score = db.Column(db.Float)
    priority_score = db.Column(db.Float)
    source = db.Column(db.String(50))
    status = db.Column(db.String(20), default='open')
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    asset = db.relationship('Asset', backref=db.backref('alerts', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'cve_id': self.cve_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'cvss_score': self.cvss_score,
            'priority_score': self.priority_score,
            'source': self.source,
            'status': self.status,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }

# Helper decorators
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

# ==================== Frontend Routes ====================

@app.route('/')
def serve_index():
    """Serve the login page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (HTML, CSS, JS)"""
    return send_from_directory(app.static_folder, path)

# ==================== API Routes ====================

# Auth routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Successfully logged out'}), 200

# User routes
@app.route('/api/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role == 'admin':
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    else:
        return jsonify([current_user.to_dict()]), 200

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if data.get('role') and current_user.role != 'admin':
        return jsonify({'error': 'Only admin can change roles'}), 403
    
    if data.get('username'):
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    if data.get('email'):
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    
    if data.get('password'):
        user.set_password(data['password'])
    
    if data.get('role') and current_user.role == 'admin':
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

# Asset routes
@app.route('/api/assets', methods=['GET'])
@jwt_required()
def list_assets():
    assets = Asset.query.all()
    return jsonify([asset.to_dict() for asset in assets]), 200

@app.route('/api/assets', methods=['POST'])
@jwt_required()
def create_asset():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Asset name required'}), 400
    
    asset = Asset(
        name=data['name'],
        hostname=data.get('hostname'),
        ip_address=data.get('ip_address'),
        asset_type=data.get('asset_type'),
        os=data.get('os'),
        firmware_version=data.get('firmware_version'),
        criticality=data.get('criticality', 'medium'),
        tags=','.join(data['tags']) if data.get('tags') else '',
        description=data.get('description')
    )
    
    db.session.add(asset)
    db.session.commit()
    
    return jsonify(asset.to_dict()), 201

@app.route('/api/assets/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    return jsonify(asset.to_dict()), 200

@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
@jwt_required()
def update_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        asset.name = data['name']
    if data.get('hostname') is not None:
        asset.hostname = data['hostname']
    if data.get('ip_address') is not None:
        asset.ip_address = data['ip_address']
    if data.get('asset_type') is not None:
        asset.asset_type = data['asset_type']
    if data.get('os') is not None:
        asset.os = data['os']
    if data.get('firmware_version') is not None:
        asset.firmware_version = data['firmware_version']
    if data.get('criticality'):
        asset.criticality = data['criticality']
    if data.get('tags') is not None:
        asset.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']
    if data.get('description') is not None:
        asset.description = data['description']
    
    db.session.commit()
    
    return jsonify(asset.to_dict()), 200

@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
@jwt_required()
def delete_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    
    db.session.delete(asset)
    db.session.commit()
    
    return jsonify({'message': 'Asset deleted successfully'}), 200

@app.route('/api/assets/import/ad', methods=['POST'])
@jwt_required()
def import_ad():
    mock_devices = [
        {'name': 'DC01', 'hostname': 'dc01.company.local', 'ip_address': '10.0.0.10', 'asset_type': 'Server', 'os': 'Windows Server 2019', 'criticality': 'critical'},
        {'name': 'FS01', 'hostname': 'fs01.company.local', 'ip_address': '10.0.0.20', 'asset_type': 'Server', 'os': 'Windows Server 2019', 'criticality': 'high'},
        {'name': 'WEB01', 'hostname': 'web01.company.local', 'ip_address': '10.0.0.30', 'asset_type': 'Server', 'os': 'Ubuntu 22.04', 'criticality': 'high'},
        {'name': 'DB01', 'hostname': 'db01.company.local', 'ip_address': '10.0.0.40', 'asset_type': 'Server', 'os': 'CentOS 8', 'criticality': 'critical'},
        {'name': 'PC-ADMIN', 'hostname': 'pc-admin.company.local', 'ip_address': '10.0.1.50', 'asset_type': 'Workstation', 'os': 'Windows 10 Pro', 'criticality': 'medium'}
    ]
    
    imported = 0
    for device in mock_devices:
        existing = Asset.query.filter_by(hostname=device['hostname']).first()
        if not existing:
            asset = Asset(**device)
            db.session.add(asset)
            imported += 1
    
    db.session.commit()
    
    return jsonify({'message': f'Successfully imported {imported} devices from Active Directory', 'imported': imported}), 200

# Alert routes
@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def list_alerts():
    status = request.args.get('status')
    severity = request.args.get('severity')
    
    query = Alert.query
    
    if status:
        query = query.filter_by(status=status)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.priority_score.desc()).all()
    
    return jsonify([alert.to_dict() for alert in alerts]), 200

@app.route('/api/alerts/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    return jsonify(alert.to_dict()), 200

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(alert.to_dict()), 200

@app.route('/api/alerts/bulk-resolve', methods=['POST'])
@jwt_required()
def bulk_resolve_alerts():
    data = request.get_json()
    alert_ids = data.get('alert_ids', [])
    
    if not alert_ids:
        return jsonify({'error': 'No alert IDs provided'}), 400
    
    alerts = Alert.query.filter(Alert.id.in_(alert_ids)).all()
    
    for alert in alerts:
        alert.status = 'resolved'
        alert.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully resolved {len(alerts)} alerts',
        'resolved_count': len(alerts)
    }), 200

@app.route('/api/alerts/statistics', methods=['GET'])
@jwt_required()
def get_alert_statistics():
    total_alerts = Alert.query.count()
    open_alerts = Alert.query.filter_by(status='open').count()
    critical_alerts = Alert.query.filter_by(severity='critical', status='open').count()
    
    return jsonify({
        'total_alerts': total_alerts,
        'open_alerts': open_alerts,
        'critical_alerts': critical_alerts
    }), 200

# Settings routes
@app.route('/api/settings', methods=['GET'])
@jwt_required()
def list_settings():
    settings = Setting.query.all()
    return jsonify([setting.to_dict() for setting in settings]), 200

@app.route('/api/settings/<string:key>', methods=['GET'])
@jwt_required()
def get_setting(key):
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        return jsonify({'error': 'Setting not found'}), 404
    return jsonify(setting.to_dict()), 200

@app.route('/api/settings/<string:key>', methods=['PUT'])
@admin_required
def update_setting(key):
    setting = Setting.query.filter_by(key=key).first()
    
    data = request.get_json()
    value = data.get('value')
    
    if value is None:
        return jsonify({'error': 'Value required'}), 400
    
    if setting:
        setting.value = str(value)
    else:
        setting = Setting(key=key, value=str(value))
        db.session.add(setting)
    
    db.session.commit()
    
    return jsonify(setting.to_dict()), 200

# Reports routes (simplified - full implementation in routes/reports.py)
@app.route('/api/reports/csv', methods=['GET'])
@jwt_required()
def export_csv():
    return jsonify({'message': 'CSV export functionality available'}), 200

@app.route('/api/reports/pdf', methods=['GET'])
@jwt_required()
def export_pdf():
    return jsonify({'message': 'PDF export functionality available'}), 200

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@assetsentinel.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            db.session.add(Setting(key='scan_interval', value='2'))
            db.session.add(Setting(key='nvd_enabled', value='true'))
            db.session.add(Setting(key='cisa_enabled', value='true'))
            
            db.session.commit()
            print("✓ Default admin user created (username: admin, password: admin123)")

if __name__ == '__main__':
    print("Initializing Asset Sentinel...")
    init_db()
    print("✓ Database initialized")
    print("")
    print("=" * 50)
    print("Asset Sentinel is running!")
    print("=" * 50)
    print("")
    print("Frontend: http://localhost:5000")
    print("Backend API: http://localhost:5000/api")
    print("")
    print("Login with:")
    print("  Username: admin")
    print("  Password: admin123")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
