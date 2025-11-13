from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

bp = Blueprint('users', __name__)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        from app import User
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    from app import User
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role == 'admin':
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    else:
        return jsonify([current_user.to_dict()]), 200

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    from app import User
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('', methods=['POST'])
@admin_required
def create_user():
    from app import User, db
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
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

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    from app import User, db
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

@bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    from app import User, db
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200
