import uuid
import os
import logging
from flask import Blueprint, jsonify, request, send_file, render_template
from app import db
from app.models.db_models import Report
from app import celery

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def index():
    """Main page with API testing interface"""
    return render_template('index.html')

@reports_bp.route('/trigger_report', methods=['POST'])
def trigger_report():
    """
    Trigger report generation as a background task.
    Returns a unique report_id for polling.
    """
    try:
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        # Create report entry in database
        report = Report(
            report_id=report_id,
            status='Running',
            report_path=None
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Try background task, fallback to synchronous execution
        try:
            celery.send_task('app.core.reporter.generate_report_task', args=[report_id])
            logging.info(f"Background task dispatched for report {report_id}")
        except Exception as redis_error:
            logging.warning(f"Redis connection failed, running synchronously: {redis_error}")
            # Fallback: Execute report generation synchronously
            try:
                from app.core.reporter import generate_report_sync
                result_path = generate_report_sync(report_id)
                logging.info(f"Synchronous report generation completed: {result_path}")
            except Exception as sync_error:
                logging.error(f"Synchronous report generation failed: {sync_error}")
                report.status = 'Failed'
                db.session.commit()
                return jsonify({
                    "error": "Report generation failed",
                    "message": str(sync_error)
                }), 500
        
        logging.info(f"Report generation triggered with ID: {report_id}")
        
        return jsonify({
            "report_id": report_id,
            "status": "Running",
            "message": "Report generation started"
        }), 200
        
    except Exception as e:
        logging.error(f"Error triggering report: {e}")
        return jsonify({
            "error": "Failed to trigger report generation",
            "message": str(e)
        }), 500

@reports_bp.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    Poll for report status and download CSV when complete.
    """
    try:
        # Find report by ID
        report = Report.query.filter_by(report_id=report_id).first()
        
        if not report:
            return jsonify({
                "error": "Report not found",
                "message": f"No report found with ID: {report_id}"
            }), 404
        
        # Check report status
        if report.status == 'Running':
            return jsonify({
                "status": "Running",
                "message": "Report is still being generated"
            }), 200
        
        elif report.status == 'Complete':
            # Check if file exists
            if not report.report_path or not os.path.exists(report.report_path):
                return jsonify({
                    "error": "Report file not found",
                    "message": "Report completed but file is missing"
                }), 500
            
            # Send CSV file
            return send_file(
                report.report_path,
                as_attachment=True,
                download_name=f'store_report_{report_id}.csv',
                mimetype='text/csv'
            )
        
        elif report.status == 'Failed':
            return jsonify({
                "status": "Failed",
                "error": "Report generation failed",
                "message": "An error occurred during report generation"
            }), 500
        
        else:
            return jsonify({
                "error": "Unknown status",
                "message": f"Report has unknown status: {report.status}"
            }), 500
            
    except Exception as e:
        logging.error(f"Error retrieving report {report_id}: {e}")
        return jsonify({
            "error": "Failed to retrieve report",
            "message": str(e)
        }), 500

@reports_bp.route('/reports', methods=['GET'])
def list_reports():
    """
    List all reports for debugging purposes.
    """
    try:
        reports = Report.query.order_by(Report.id.desc()).limit(50).all()
        
        report_list = []
        for report in reports:
            report_list.append({
                "report_id": report.report_id,
                "status": report.status,
                "report_path": report.report_path,
                "created_at": report.id  # Using ID as a proxy for creation order
            })
        
        return jsonify({
            "reports": report_list,
            "count": len(report_list)
        }), 200
        
    except Exception as e:
        logging.error(f"Error listing reports: {e}")
        return jsonify({
            "error": "Failed to list reports",
            "message": str(e)
        }), 500
