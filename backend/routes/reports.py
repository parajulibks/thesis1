from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
# from models import Alert, Asset
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime, timedelta
import csv
import io
import os

bp = Blueprint('reports', __name__)

@bp.route('/pdf', methods=['GET'])
@jwt_required()
def generate_pdf_report():
    """Generate PDF report of top 10 critical vulnerabilities"""
    # Get critical alerts from the past week
    week_ago = datetime.utcnow() - timedelta(days=7)
    alerts = Alert.query.filter(
        Alert.severity == 'critical',
        Alert.status == 'open',
        Alert.detected_at >= week_ago
    ).order_by(Alert.priority_score.desc()).limit(10).all()
    
    # Create PDF
    filename = f'/tmp/vulnerability_report_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Asset Sentinel - Weekly Vulnerability Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Date
    date_text = Paragraph(f"Report Date: {datetime.utcnow().strftime('%Y-%m-%d')}", styles['Normal'])
    story.append(date_text)
    story.append(Spacer(1, 12))
    
    # Executive Summary
    summary_title = Paragraph("Executive Summary", styles['Heading2'])
    story.append(summary_title)
    
    total_assets = Asset.query.count()
    total_critical = len(alerts)
    
    summary_text = f"""
    This report provides an overview of the top 10 critical vulnerabilities detected in the past week.
    <br/><br/>
    Total Assets Monitored: {total_assets}<br/>
    Critical Vulnerabilities Detected: {total_critical}<br/>
    """
    
    summary = Paragraph(summary_text, styles['Normal'])
    story.append(summary)
    story.append(Spacer(1, 20))
    
    # Top 10 Critical Vulnerabilities
    vulns_title = Paragraph("Top 10 Critical Vulnerabilities", styles['Heading2'])
    story.append(vulns_title)
    story.append(Spacer(1, 12))
    
    if alerts:
        data = [['CVE ID', 'Asset', 'CVSS', 'Priority', 'Source']]
        
        for alert in alerts:
            data.append([
                alert.cve_id or 'N/A',
                alert.asset.name if alert.asset else 'N/A',
                str(alert.cvss_score) if alert.cvss_score else 'N/A',
                str(alert.priority_score) if alert.priority_score else 'N/A',
                alert.source or 'N/A'
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        no_vulns = Paragraph("No critical vulnerabilities detected in the past week.", styles['Normal'])
        story.append(no_vulns)
    
    # Build PDF
    doc.build(story)
    
    return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))

@bp.route('/csv', methods=['GET'])
@jwt_required()
def generate_csv_export():
    """Export alerts to CSV"""
    alerts = Alert.query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Asset Name', 'CVE ID', 'Title', 'Severity', 
        'CVSS Score', 'Priority Score', 'Source', 'Status', 
        'Detected At', 'Resolved At'
    ])
    
    # Write data
    for alert in alerts:
        writer.writerow([
            alert.id,
            alert.asset.name if alert.asset else 'N/A',
            alert.cve_id or 'N/A',
            alert.title,
            alert.severity,
            alert.cvss_score or 'N/A',
            alert.priority_score or 'N/A',
            alert.source or 'N/A',
            alert.status,
            alert.detected_at.strftime('%Y-%m-%d %H:%M:%S') if alert.detected_at else 'N/A',
            alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if alert.resolved_at else 'N/A'
        ])
    
    # Prepare response
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'alerts_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'
    )
