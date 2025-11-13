"""
Asset Sentinel - Integrated Backend with Simple Session-Based Authentication
This file serves both the API endpoints and the frontend static files
No JWT - uses Flask sessions for authentication
"""

from flask import Flask, jsonify, request, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps
import os
import secrets

load_dotenv()

# Initialize Flask app with static folder pointing to frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///asset_sentinel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

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
            'created_at': self.created_at.strftime('%m/%d/%Y')
        }

class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    asset_type = db.Column(db.String(50))
    os = db.Column(db.String(100))
    firmware_version = db.Column(db.String(50))
    criticality = db.Column(db.String(20), default='low')
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'type': self.asset_type,
            'os': self.os,
            'firmware_version': self.firmware_version,
            'criticality': self.criticality,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    cve_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))
    cvss_score = db.Column(db.Float)
    priority_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')
    source = db.Column(db.String(50))
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        asset = Asset.query.get(self.asset_id)
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': asset.name if asset else 'Unknown',
            'cve_id': self.cve_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'cvss_score': self.cvss_score,
            'priority_score': self.priority_score,
            'status': self.status,
            'source': self.source,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }

# Authentication decorator
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(session['user_id'])
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
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create session
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session.permanent = True
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

# User routes
@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    
    if 'role' in data:
        user.role = data['role']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict()), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

# Asset routes
@app.route('/api/assets', methods=['GET'])
@login_required
def get_assets():
    assets = Asset.query.all()
    return jsonify([asset.to_dict() for asset in assets]), 200

@app.route('/api/assets/<int:asset_id>', methods=['GET'])
@login_required
def get_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return jsonify(asset.to_dict()), 200

@app.route('/api/assets', methods=['POST'])
@login_required
def create_asset():
    data = request.get_json()
    asset = Asset(
        name=data['name'],
        hostname=data.get('hostname'),
        ip_address=data.get('ip_address'),
        asset_type=data.get('type'),
        os=data.get('os'),
        firmware_version=data.get('firmware_version'),
        criticality=data.get('criticality', 'low'),
        tags=data.get('tags')
    )
    db.session.add(asset)
    db.session.commit()
    return jsonify(asset.to_dict()), 201

@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
@login_required
def update_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.get_json()
    
    asset.name = data.get('name', asset.name)
    asset.hostname = data.get('hostname', asset.hostname)
    asset.ip_address = data.get('ip_address', asset.ip_address)
    asset.asset_type = data.get('type', asset.asset_type)
    asset.os = data.get('os', asset.os)
    asset.firmware_version = data.get('firmware_version', asset.firmware_version)
    asset.criticality = data.get('criticality', asset.criticality)
    asset.tags = data.get('tags', asset.tags)
    asset.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(asset.to_dict()), 200

@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
@login_required
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Asset deleted'}), 200

@app.route('/api/assets/import/ad', methods=['POST'])
@login_required
def import_from_ad():
    """Mock AD import - creates 5 sample devices"""
    sample_devices = [
        {'name': 'DC01', 'hostname': 'dc01.company.local', 'ip_address': '10.0.0.10', 
         'asset_type': 'Server', 'os': 'Windows Server 2019', 'criticality': 'critical'},
        {'name': 'FS01', 'hostname': 'fs01.company.local', 'ip_address': '10.0.0.20',
         'asset_type': 'Server', 'os': 'Windows Server 2019', 'criticality': 'high'},
        {'name': 'WEB01', 'hostname': 'web01.company.local', 'ip_address': '10.0.0.30',
         'asset_type': 'Server', 'os': 'Ubuntu 22.04', 'criticality': 'high'},
        {'name': 'DB01', 'hostname': 'db01.company.local', 'ip_address': '10.0.0.40',
         'asset_type': 'Server', 'os': 'CentOS 8', 'criticality': 'critical'},
        {'name': 'PC-ADMIN', 'hostname': 'pc-admin.company.local', 'ip_address': '10.0.1.50',
         'asset_type': 'Workstation', 'os': 'Windows 10 Pro', 'criticality': 'medium'}
    ]
    
    imported_count = 0
    for device_data in sample_devices:
        # Check if asset already exists
        existing = Asset.query.filter_by(name=device_data['name']).first()
        if not existing:
            asset = Asset(**device_data)
            db.session.add(asset)
            imported_count += 1
    
    db.session.commit()
    return jsonify({'message': f'Successfully imported {imported_count} devices'}), 200

# Alert routes
@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    status = request.args.get('status')
    query = Alert.query
    if status:
        query = query.filter_by(status=status)
    alerts = query.all()
    return jsonify([alert.to_dict() for alert in alerts]), 200

@app.route('/api/alerts/statistics', methods=['GET'])
@login_required
def get_alert_statistics():
    total = Alert.query.count()
    critical = Alert.query.filter_by(severity='critical').count()
    open_alerts = Alert.query.filter_by(status='open').count()
    
    return jsonify({
        'total': total,
        'critical': critical,
        'open': open_alerts
    }), 200

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify(alert.to_dict()), 200

# Settings routes
@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    settings = Setting.query.all()
    return jsonify([s.to_dict() for s in settings]), 200

@app.route('/api/settings', methods=['POST'])
@admin_required
def update_settings():
    data = request.get_json()
    for key, value in data.items():
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
    db.session.commit()
    return jsonify({'message': 'Settings updated'}), 200

@app.route('/api/settings/<key>', methods=['PUT'])
@admin_required
def update_setting(key):
    """Update a single setting"""
    data = request.get_json()
    value = data.get('value', '')
    
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = str(value)
    else:
        setting = Setting(key=key, value=str(value))
        db.session.add(setting)
    db.session.commit()
    return jsonify(setting.to_dict()), 200

# Vulnerability scanning routes
@app.route('/api/vulnerabilities/scan', methods=['POST'])
@admin_required
def manual_vulnerability_scan():
    """Manually trigger vulnerability scan for all assets"""
    try:
        assets = Asset.query.all()
        scan_results = {'scanned': 0, 'vulnerabilities_found': 0, 'errors': 0}
        
        for asset in assets:
            try:
                # Scan for vulnerabilities
                vulns = scan_asset_vulnerabilities(asset)
                scan_results['scanned'] += 1
                
                # Create alerts for found vulnerabilities
                for vuln_data in vulns:
                    # Check if alert already exists
                    existing = Alert.query.filter_by(
                        asset_id=asset.id,
                        cve_id=vuln_data['cve_id']
                    ).first()
                    
                    if not existing:
                        alert = Alert(
                            asset_id=asset.id,
                            cve_id=vuln_data['cve_id'],
                            title=vuln_data.get('title', ''),
                            description=vuln_data.get('description', ''),
                            severity=vuln_data.get('severity', 'medium'),
                            cvss_score=vuln_data.get('cvss_score', 0.0),
                            priority_score=vuln_data.get('priority_score', 0.0),
                            source=vuln_data.get('source', 'Manual Scan'),
                            status='open'
                        )
                        db.session.add(alert)
                        scan_results['vulnerabilities_found'] += 1
                
            except Exception as e:
                print(f"Error scanning asset {asset.id}: {e}")
                scan_results['errors'] += 1
        
        db.session.commit()
        return jsonify({
            'message': 'Scan completed',
            'results': scan_results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vulnerabilities/search', methods=['POST'])
@login_required
def search_vulnerabilities():
    """Search for vulnerabilities by product name and version using NVD API"""
    try:
        data = request.get_json()
        product = data.get('product', '').strip()
        version = data.get('version', '').strip()
        
        if not product:
            return jsonify({'error': 'Product name is required'}), 400
        
        # Call NVD API
        results = search_nvd_by_product(product, version)
        
        return jsonify({
            'product': product,
            'version': version,
            'vulnerabilities': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def search_nvd_by_product(product, version=None):
    """Search NVD API for vulnerabilities by product name and version"""
    import requests
    import time
    
    try:
        # NVD API endpoint
        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # Build search query
        params = {
            'keywordSearch': product,
            'resultsPerPage': 10
        }
        
        if version:
            params['keywordSearch'] = f"{product} {version}"
        
        # Make request to NVD API
        response = requests.get(base_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            vulnerabilities = []
            
            if 'vulnerabilities' in data:
                for item in data['vulnerabilities']:
                    cve = item.get('cve', {})
                    cve_id = cve.get('id', 'Unknown')
                    
                    # Extract description
                    descriptions = cve.get('descriptions', [])
                    description = next((d['value'] for d in descriptions if d['lang'] == 'en'), 'No description available')
                    
                    # Extract CVSS score
                    metrics = cve.get('metrics', {})
                    cvss_score = 0.0
                    severity = 'MEDIUM'
                    
                    if 'cvssMetricV31' in metrics and metrics['cvssMetricV31']:
                        cvss_data = metrics['cvssMetricV31'][0]['cvssData']
                        cvss_score = cvss_data.get('baseScore', 0.0)
                        severity = cvss_data.get('baseSeverity', 'MEDIUM')
                    elif 'cvssMetricV2' in metrics and metrics['cvssMetricV2']:
                        cvss_score = metrics['cvssMetricV2'][0]['cvssData'].get('baseScore', 0.0)
                        if cvss_score >= 7.0:
                            severity = 'HIGH'
                        elif cvss_score >= 4.0:
                            severity = 'MEDIUM'
                        else:
                            severity = 'LOW'
                    
                    # Extract published date
                    published = cve.get('published', '')
                    
                    vulnerabilities.append({
                        'cve_id': cve_id,
                        'description': description[:500],  # Limit description length
                        'cvss_score': cvss_score,
                        'severity': severity,
                        'published': published,
                        'source': 'NVD',
                        'url': f'https://nvd.nist.gov/vuln/detail/{cve_id}'
                    })
            
            return vulnerabilities
        else:
            return []
            
    except Exception as e:
        print(f"Error searching NVD: {e}")
        return []

def scan_asset_vulnerabilities(asset):
    """Scan an asset for vulnerabilities using its OS and software info"""
    vulnerabilities = []
    
    # Extract product info from asset
    if asset.os:
        # Search for OS vulnerabilities
        os_parts = asset.os.lower().split()
        if os_parts:
            product = os_parts[0]  # e.g., "Windows", "Ubuntu", "CentOS"
            version = ""
            
            # Try to extract version
            for part in os_parts[1:]:
                if any(c.isdigit() for c in part):
                    version = part
                    break
            
            # Search NVD for this product
            nvd_results = search_nvd_by_product(product, version)
            
            # Convert to alert format and calculate priority
            for vuln in nvd_results[:5]:  # Limit to top 5 results
                # Calculate priority score
                cvss = vuln.get('cvss_score', 0.0)
                
                # Criticality weights
                criticality_weight = {
                    'low': 0.2,
                    'medium': 0.5,
                    'high': 0.75,
                    'critical': 1.0
                }.get(asset.criticality, 0.5)
                
                # Priority calculation
                priority = (cvss / 10.0 * 50) + (0.8 * 30) + (criticality_weight * 20)
                
                vulnerabilities.append({
                    'cve_id': vuln['cve_id'],
                    'title': f"Vulnerability in {product}",
                    'description': vuln['description'],
                    'severity': vuln['severity'].lower(),
                    'cvss_score': cvss,
                    'priority_score': round(priority, 2),
                    'source': 'NVD API',
                    'url': vuln['url']
                })
    
    return vulnerabilities

# Report routes
@app.route('/api/reports/pdf', methods=['GET'])
@login_required
def generate_pdf_report():
    return jsonify({'message': 'PDF report generation not yet implemented'}), 501

@app.route('/api/reports/csv', methods=['GET'])
@login_required
def generate_csv_report():
    return jsonify({'message': 'CSV export not yet implemented'}), 501

# ==================== Database Initialization ====================

def init_database():
    """Initialize database and create default admin user"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@assetsentinel.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✓ Default admin user created (username: admin, password: admin123)')
        else:
            print('✓ Database initialized')

# ==================== Application Startup ====================

if __name__ == '__main__':
    print('Initializing Asset Sentinel...')
    init_database()
    
    print('\n' + '='*50)
    print('Asset Sentinel is running!')
    print('='*50)
    print('\nFrontend: http://localhost:5000')
    print('Backend API: http://localhost:5000/api')
    print('\nLogin with:')
    print('  Username: admin')
    print('  Password: admin123')
    print('\nPress Ctrl+C to stop the server')
    print('='*50 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
