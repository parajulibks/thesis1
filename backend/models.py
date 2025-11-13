from datetime import datetime

# Models will be defined after app initialization
# Import db and bcrypt from app when needed

def get_db_bcrypt():
    """Get db and bcrypt from app"""
    import app as app_module
    return app_module.db, app_module.bcrypt

class User:
    """User model - will be defined dynamically"""
    pass

class Asset:
    """Asset model - will be defined dynamically"""
    pass

class Alert:
    """Alert model - will be defined dynamically"""
    pass

class Setting:
    """Setting model - will be defined dynamically"""
    pass

def create_models(db, bcrypt):
    """Create model classes with db and bcrypt"""
    
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), nullable=False, default='user')  # admin, user, viewer
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
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
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
        criticality = db.Column(db.String(20), default='medium')  # low, medium, high, critical
        tags = db.Column(db.Text)  # Comma-separated tags
        description = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        alerts = db.relationship('Alert', backref='asset', lazy=True, cascade='all, delete-orphan')
        
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
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    class Alert(db.Model):
        __tablename__ = 'alerts'
        
        id = db.Column(db.Integer, primary_key=True)
        asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
        cve_id = db.Column(db.String(20))
        title = db.Column(db.String(500), nullable=False)
        description = db.Column(db.Text)
        severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
        cvss_score = db.Column(db.Float)
        priority_score = db.Column(db.Float)
        source = db.Column(db.String(50))  # NVD, CISA, OSV, Vulners, Vendor
        cpe_match = db.Column(db.String(500))
        confidence = db.Column(db.String(20))  # low, medium, high
        patch_url = db.Column(db.Text)
        exploitability = db.Column(db.String(20))
        status = db.Column(db.String(20), default='open')  # open, resolved
        detected_at = db.Column(db.DateTime, default=datetime.utcnow)
        resolved_at = db.Column(db.DateTime)
        
        def calculate_priority(self):
            """Calculate priority score based on CVSS, exploitability, and asset criticality"""
            priority = 0.0
            
            # CVSS score weight (50%)
            if self.cvss_score:
                priority += (self.cvss_score / 10.0) * 50
            
            # Exploitability weight (30%)
            exploitability_weights = {
                'high': 30,
                'medium': 20,
                'low': 10
            }
            if self.exploitability:
                priority += exploitability_weights.get(self.exploitability.lower(), 0)
            
            # Asset criticality weight (20%)
            if self.asset:
                criticality_weights = {
                    'critical': 20,
                    'high': 15,
                    'medium': 10,
                    'low': 5
                }
                priority += criticality_weights.get(self.asset.criticality.lower(), 0)
            
            self.priority_score = round(priority, 2)
            return self.priority_score
        
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
                'cpe_match': self.cpe_match,
                'confidence': self.confidence,
                'patch_url': self.patch_url,
                'exploitability': self.exploitability,
                'status': self.status,
                'detected_at': self.detected_at.isoformat() if self.detected_at else None,
                'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
            }

    class Setting(db.Model):
        __tablename__ = 'settings'
        
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(100), unique=True, nullable=False)
        value = db.Column(db.Text)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'key': self.key,
                'value': self.value,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
    
    return User, Asset, Alert, Setting
