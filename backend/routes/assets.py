from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import csv
import io

bp = Blueprint('assets', __name__)

def check_permission(action):
    """Check if user has permission for the action"""
    from app import User
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
def list_assets():
    """List all assets"""
    from app import Asset
    assets = Asset.query.all()
    return jsonify([asset.to_dict() for asset in assets]), 200

@bp.route('/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_asset(asset_id):
    """Get a specific asset"""
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    
    return jsonify(asset.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_asset():
    """Create a new asset"""
    has_permission, user = check_permission('create')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
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

@bp.route('/<int:asset_id>', methods=['PUT'])
@jwt_required()
def update_asset(asset_id):
    """Update an asset"""
    has_permission, user = check_permission('update')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
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

@bp.route('/<int:asset_id>', methods=['DELETE'])
@jwt_required()
def delete_asset(asset_id):
    """Delete an asset"""
    has_permission, user = check_permission('delete')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    
    db.session.delete(asset)
    db.session.commit()
    
    return jsonify({'message': 'Asset deleted successfully'}), 200

@bp.route('/import/csv', methods=['POST'])
@jwt_required()
def import_csv():
    """Import assets from CSV file"""
    has_permission, user = check_permission('create')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                if not row.get('name'):
                    errors.append(f"Row {row_num}: Name is required")
                    continue
                
                asset = Asset(
                    name=row['name'],
                    hostname=row.get('hostname'),
                    ip_address=row.get('ip_address'),
                    asset_type=row.get('asset_type'),
                    os=row.get('os'),
                    firmware_version=row.get('firmware_version'),
                    criticality=row.get('criticality', 'medium'),
                    tags=row.get('tags', ''),
                    description=row.get('description')
                )
                
                db.session.add(asset)
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully imported {imported} assets',
            'imported': imported,
            'errors': errors
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to import CSV: {str(e)}'}), 400

@bp.route('/import/ad', methods=['POST'])
@jwt_required()
def import_active_directory():
    """Import assets from Active Directory (Mock)"""
    has_permission, user = check_permission('create')
    if not has_permission:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Mock AD import - in production, this would connect to LDAP
    mock_devices = [
        {
            'name': 'DC01',
            'hostname': 'dc01.company.local',
            'ip_address': '10.0.0.10',
            'asset_type': 'Server',
            'os': 'Windows Server 2019',
            'criticality': 'critical'
        },
        {
            'name': 'FS01',
            'hostname': 'fs01.company.local',
            'ip_address': '10.0.0.20',
            'asset_type': 'Server',
            'os': 'Windows Server 2019',
            'criticality': 'high'
        },
        {
            'name': 'WEB01',
            'hostname': 'web01.company.local',
            'ip_address': '10.0.0.30',
            'asset_type': 'Server',
            'os': 'Ubuntu 22.04',
            'criticality': 'high'
        },
        {
            'name': 'DB01',
            'hostname': 'db01.company.local',
            'ip_address': '10.0.0.40',
            'asset_type': 'Server',
            'os': 'CentOS 8',
            'criticality': 'critical'
        },
        {
            'name': 'PC-ADMIN',
            'hostname': 'pc-admin.company.local',
            'ip_address': '10.0.1.50',
            'asset_type': 'Workstation',
            'os': 'Windows 10 Pro',
            'criticality': 'medium'
        }
    ]
    
    imported = 0
    for device in mock_devices:
        # Check if asset already exists
        existing = Asset.query.filter_by(hostname=device['hostname']).first()
        if not existing:
            asset = Asset(**device)
            db.session.add(asset)
            imported += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully imported {imported} devices from Active Directory',
        'imported': imported
    }), 200
