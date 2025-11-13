from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Alert, Asset
from app import db
from datetime import datetime

bp = Blueprint('alerts', __name__)

def check_permission(action):
    """Check if user has permission for the action"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return False, None
    
    # Viewer can only read
    if user.role == 'viewer' and action not in ['read']:
        return False, user
    
    return True, user

@bp.route('', methods=['GET'])
@jwt_required()
def list_alerts():
    """List all alerts with optional filtering"""
    status = request.args.get('status')
    severity = request.args.get('severity')
    
    query = Alert.query
    
    if status:
        query = query.filter_by(status=status)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.priority_score.desc()).all()
    
    return jsonify([alert.to_dict() for alert in alerts]), 200

@bp.route('/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    """Get a specific alert"""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    return jsonify(alert.to_dict()), 200

@bp.route('/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    """Mark an alert as resolved"""
    has_permission, user = check_permission('update')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(alert.to_dict()), 200

@bp.route('/bulk-resolve', methods=['POST'])
@jwt_required()
def bulk_resolve_alerts():
    """Mark multiple alerts as resolved"""
    has_permission, user = check_permission('update')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
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

@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get alert statistics"""
    total_alerts = Alert.query.count()
    open_alerts = Alert.query.filter_by(status='open').count()
    critical_alerts = Alert.query.filter_by(severity='critical', status='open').count()
    
    return jsonify({
        'total_alerts': total_alerts,
        'open_alerts': open_alerts,
        'critical_alerts': critical_alerts
    }), 200
