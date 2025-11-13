from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Setting
from app import db

bp = Blueprint('settings', __name__)

def admin_required():
    """Check if user is admin"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.role == 'admin'

@bp.route('', methods=['GET'])
@jwt_required()
def list_settings():
    """List all settings"""
    settings = Setting.query.all()
    return jsonify([setting.to_dict() for setting in settings]), 200

@bp.route('/<string:key>', methods=['GET'])
@jwt_required()
def get_setting(key):
    """Get a specific setting"""
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        return jsonify({'error': 'Setting not found'}), 404
    
    return jsonify(setting.to_dict()), 200

@bp.route('/<string:key>', methods=['PUT'])
@jwt_required()
def update_setting(key):
    """Update a setting (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
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

@bp.route('', methods=['POST'])
@jwt_required()
def create_setting():
    """Create a new setting (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('key'):
        return jsonify({'error': 'Key is required'}), 400
    
    # Check if setting already exists
    existing = Setting.query.filter_by(key=data['key']).first()
    if existing:
        return jsonify({'error': 'Setting already exists'}), 400
    
    setting = Setting(
        key=data['key'],
        value=data.get('value', '')
    )
    
    db.session.add(setting)
    db.session.commit()
    
    return jsonify(setting.to_dict()), 201
