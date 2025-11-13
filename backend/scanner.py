import requests
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime

def send_webhook_notification(alert):
    """Send webhook notification for critical/high severity alerts"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        return
    
    if alert.severity not in ['critical', 'high']:
        return
    
    try:
        payload = {
            'alert_id': alert.id,
            'asset_name': alert.asset.name if alert.asset else 'Unknown',
            'cve_id': alert.cve_id,
            'title': alert.title,
            'severity': alert.severity,
            'cvss_score': alert.cvss_score,
            'priority_score': alert.priority_score,
            'detected_at': alert.detected_at.isoformat() if alert.detected_at else None
        }
        
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send webhook notification: {e}")

def scan_nvd_vulnerabilities(asset):
    """Scan NVD for vulnerabilities matching asset"""
    from app import Setting
    try:
        # Check if NVD is enabled
        nvd_enabled = Setting.query.filter_by(key='nvd_enabled').first()
        if not nvd_enabled or nvd_enabled.value.lower() != 'true':
            return []
        
        # This is a simplified version - in production, you would:
        # 1. Parse asset OS/software to CPE format
        # 2. Query NVD API with CPE
        # 3. Parse and store vulnerability data
        
        # For demo purposes, we'll create mock data
        if asset.os and 'windows' in asset.os.lower():
            vulnerabilities = [
                {
                    'cve_id': 'CVE-2024-21351',
                    'title': 'Windows Remote Code Execution Vulnerability',
                    'description': 'A remote code execution vulnerability exists in Windows',
                    'severity': 'critical',
                    'cvss_score': 9.8,
                    'source': 'NVD',
                    'cpe_match': 'cpe:2.3:o:microsoft:windows',
                    'confidence': 'high',
                    'exploitability': 'high',
                    'patch_url': 'https://msrc.microsoft.com/update-guide'
                }
            ]
            return vulnerabilities
        
        return []
        
    except Exception as e:
        print(f"Error scanning NVD for asset {asset.id}: {e}")
        return []

def scan_cisa_kev(asset):
    """Scan CISA Known Exploited Vulnerabilities"""
    from app import Setting
    try:
        # Check if CISA is enabled
        cisa_enabled = Setting.query.filter_by(key='cisa_enabled').first()
        if not cisa_enabled or cisa_enabled.value.lower() != 'true':
            return []
        
        # In production, fetch from https://www.cisa.gov/known-exploited-vulnerabilities-catalog
        # For demo, return mock data
        
        if asset.asset_type and 'server' in asset.asset_type.lower():
            vulnerabilities = [
                {
                    'cve_id': 'CVE-2024-23897',
                    'title': 'Jenkins Arbitrary File Read Vulnerability',
                    'description': 'Critical vulnerability in Jenkins allowing arbitrary file read',
                    'severity': 'high',
                    'cvss_score': 8.5,
                    'source': 'CISA KEV',
                    'cpe_match': 'cpe:2.3:a:jenkins:jenkins',
                    'confidence': 'medium',
                    'exploitability': 'high',
                    'patch_url': 'https://www.jenkins.io/security/advisory/'
                }
            ]
            return vulnerabilities
        
        return []
        
    except Exception as e:
        print(f"Error scanning CISA KEV for asset {asset.id}: {e}")
        return []

def scan_osv_vulnerabilities(asset):
    """Scan OSV for vulnerabilities"""
    try:
        # In production, query OSV API: https://osv.dev/
        # For demo, return mock data for specific OS types
        
        if asset.os and 'ubuntu' in asset.os.lower():
            vulnerabilities = [
                {
                    'cve_id': 'CVE-2024-1086',
                    'title': 'Linux Kernel Use-After-Free Vulnerability',
                    'description': 'Use-after-free vulnerability in Linux kernel netfilter',
                    'severity': 'high',
                    'cvss_score': 7.8,
                    'source': 'OSV',
                    'cpe_match': 'cpe:2.3:o:linux:linux_kernel',
                    'confidence': 'high',
                    'exploitability': 'medium',
                    'patch_url': 'https://ubuntu.com/security/notices'
                }
            ]
            return vulnerabilities
        
        return []
        
    except Exception as e:
        print(f"Error scanning OSV for asset {asset.id}: {e}")
        return []

def perform_vulnerability_scan():
    """Main vulnerability scanning function"""
    from app import Asset, Alert, db
    print(f"Starting vulnerability scan at {datetime.utcnow()}")
    
    try:
        assets = Asset.query.all()
        
        for asset in assets:
            # Scan multiple sources
            all_vulnerabilities = []
            all_vulnerabilities.extend(scan_nvd_vulnerabilities(asset))
            all_vulnerabilities.extend(scan_cisa_kev(asset))
            all_vulnerabilities.extend(scan_osv_vulnerabilities(asset))
            
            # Create or update alerts
            for vuln in all_vulnerabilities:
                # Check if alert already exists
                existing = Alert.query.filter_by(
                    asset_id=asset.id,
                    cve_id=vuln['cve_id']
                ).first()
                
                if not existing:
                    alert = Alert(
                        asset_id=asset.id,
                        cve_id=vuln['cve_id'],
                        title=vuln['title'],
                        description=vuln['description'],
                        severity=vuln['severity'],
                        cvss_score=vuln['cvss_score'],
                        source=vuln['source'],
                        cpe_match=vuln['cpe_match'],
                        confidence=vuln['confidence'],
                        exploitability=vuln['exploitability'],
                        patch_url=vuln['patch_url'],
                        status='open'
                    )
                    
                    # Calculate priority
                    alert.calculate_priority()
                    
                    db.session.add(alert)
                    db.session.commit()
                    
                    # Send webhook notification
                    send_webhook_notification(alert)
                    
                    print(f"Created alert {alert.id} for asset {asset.name}: {alert.cve_id}")
        
        print(f"Vulnerability scan completed at {datetime.utcnow()}")
        
    except Exception as e:
        print(f"Error during vulnerability scan: {e}")
        db.session.rollback()

def start_background_scanner(app):
    """Start the background vulnerability scanner"""
    from app import Setting
    # Get scan interval from settings
    with app.app_context():
        scan_interval_setting = Setting.query.filter_by(key='scan_interval').first()
        scan_interval = int(scan_interval_setting.value) if scan_interval_setting else 2
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: app.app_context().__enter__() or perform_vulnerability_scan(),
        trigger="interval",
        minutes=scan_interval,
        id='vulnerability_scan',
        name='Scan for vulnerabilities every N minutes',
        replace_existing=True
    )
    scheduler.start()
    
    print(f"Background vulnerability scanner started (interval: {scan_interval} minutes)")
    
    # Perform initial scan
    with app.app_context():
        perform_vulnerability_scan()
