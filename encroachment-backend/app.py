"""
MAIN FLASK APPLICATION
Connects all modules together and provides REST API endpoints

MODULES USED:
1. database.py - Database operations
2. detection.py - Building detection (OpenCV)
3. encroachment.py - Overlap checking
4. reporting.py - PDF/CSV reports
5. admin_review.py - Verification system

BEGINNER-FRIENDLY:
- Clear comments explaining each part
- Simple error handling
- Easy to understand flow
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, 
    jwt_required, get_jwt_identity
)
from werkzeug.utils import secure_filename
import os
import json
import cv2
from datetime import datetime

# Import configuration
from config import Config

# Import database functions
from database import (
    get_db_connection, close_db_connection,
    create_user, get_user_by_email, get_user_by_id,
    create_image, get_image, get_all_images, update_image_processed, delete_image,
    create_detection, get_detection, get_all_detections,
    create_encroachment, get_encroachment, get_all_encroachments,
    verify_encroachment, get_pending_encroachments,
    get_statistics
)

# Import detection modules
from detection import BuildingDetector
from encroachment import EncroachmentChecker
from reporting import ReportGenerator
from admin_review import AdminReview

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE

# Enable CORS (allows frontend to connect)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# JWT for authentication
jwt = JWTManager(app)

# Create upload folders
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs('uploads/masks', exist_ok=True)
os.makedirs('uploads/visualizations', exist_ok=True)
os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)

# Initialize modules
building_detector = BuildingDetector()
encroachment_checker = EncroachmentChecker()
report_generator = ReportGenerator()
admin_reviewer = AdminReview()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """
    Save uploaded file with unique name.
    
    Returns:
        (filename, filepath) tuple
    """
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    return unique_filename, filepath


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register new user
    
    Request body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        }
    """
    try:
        data = request.json
        
        # Validate input
        if not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Create user
        result = create_user(
            name=data['name'],
            email=data['email'],
            password=data['password'],  # In production, hash this!
            role='user'
        )
        
        if not result['success']:
            return jsonify({'message': result['error']}), 400
        
        # Get created user
        user = get_user_by_id(result['user_id'])
        
        # Create JWT token
        token = create_access_token(identity=user['id'])
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login user
    
    Request body:
        {
            "email": "admin@example.com",
            "password": "admin123"
        }
    """
    try:
        data = request.json
        
        # Validate input
        if not all(k in data for k in ['email', 'password']):
            return jsonify({'message': 'Missing email or password'}), 400
        
        # Find user
        user = get_user_by_email(data['email'])
        
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check password (in production, use hashed passwords!)
        if user['password'] != data['password']:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Create JWT token
        token = create_access_token(identity=user['id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current logged-in user info
    Requires JWT token in header
    """
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# IMAGE UPLOAD ROUTES
# ============================================================================

@app.route('/api/images/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """
    Upload an image for detection
    
    Form data:
        file: Image file
        image_type: 'satellite' | 'drone' | 'cctv' | 'mobile'
        location: Optional location description
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
    """
    try:
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'Invalid file type'}), 400
        
        # Save file
        filename, filepath = save_uploaded_file(file)
        
        # Get metadata
        image_type = request.form.get('image_type', 'satellite')
        location = request.form.get('location')
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Save to database
        image_id = create_image(
            filename=filename,
            filepath=filepath,
            image_type=image_type,
            user_id=user_id,
            location=location,
            latitude=latitude,
            longitude=longitude
        )
        
        # Get saved image
        image = get_image(image_id)
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'image': image
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/images', methods=['GET'])
@jwt_required()
def get_images():
    """Get all uploaded images"""
    try:
        images = get_all_images()
        return jsonify(images), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/images/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image_by_id(image_id):
    """Get specific image by ID"""
    try:
        image = get_image(image_id)
        if not image:
            return jsonify({'message': 'Image not found'}), 404
        return jsonify(image), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image_by_id(image_id):
    """Delete image"""
    try:
        image = get_image(image_id)
        if not image:
            return jsonify({'message': 'Image not found'}), 404
        
        # Delete file from disk
        if os.path.exists(image['filepath']):
            os.remove(image['filepath'])
        
        # Delete from database
        delete_image(image_id)
        
        return jsonify({'message': 'Image deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# DETECTION ROUTES (Building Detection)
# ============================================================================

@app.route('/api/detection/run', methods=['POST'])
@jwt_required()
def run_detection():
    """
    Run building detection on an image
    
    Request body:
        {
            "image_id": 1
        }
    """
    try:
        data = request.json
        image_id = data.get('image_id')
        
        if not image_id:
            return jsonify({'message': 'image_id required'}), 400
        
        # Get image
        image = get_image(image_id)
        if not image:
            return jsonify({'message': 'Image not found'}), 404
        
        # Run detection (MODULE 2)
        print(f"Running detection on: {image['filepath']}")
        result = building_detector.detect_and_analyze(image['filepath'])
        
        # Save mask and visualization
        mask_filename = f"mask_{image['filename']}"
        mask_path = os.path.join('uploads/masks', mask_filename)
        cv2.imwrite(mask_path, result['mask'])
        
        vis_filename = f"vis_{image['filename']}"
        vis_path = os.path.join('uploads/visualizations', vis_filename)
        cv2.imwrite(vis_path, result['visualization'])
        
        # Prepare detection data (remove numpy arrays for JSON)
        detection_data = {
            'num_buildings': result['num_buildings'],
            'total_area': result['total_area'],
            'buildings': []
        }
        
        for building in result['buildings']:
            detection_data['buildings'].append({
                'id': building['id'],
                'bbox': building['bbox'],
                'area': building['area'],
                'center': building['center']
            })
        
        # Save to database
        detection_id = create_detection(
            image_id=image_id,
            num_buildings=result['num_buildings'],
            total_area=result['total_area'],
            detection_data=json.dumps(detection_data),
            mask_path=mask_path
        )
        
        # Mark image as processed
        update_image_processed(image_id)
        
        # Check for encroachments (MODULE 3)
        print("Checking for encroachments...")
        enc_result = encroachment_checker.analyze_image_detections(result)
        
        # Save encroachments to database
        for enc in enc_result['encroachments']:
            create_encroachment(
                detection_id=detection_id,
                building_id=enc['building_id'],
                is_encroachment=1,
                overlap_percentage=enc['overlap_percentage'],
                zone_name=enc['zone_name'],
                severity=enc['severity']
            )
        
        return jsonify({
            'message': 'Detection completed',
            'detection_id': detection_id,
            'num_buildings': result['num_buildings'],
            'total_area': result['total_area'],
            'mask_path': mask_path,
            'visualization_path': vis_path,
            'encroachments_found': enc_result['total_encroachments'],
            'buildings': detection_data['buildings']
        }), 200
        
    except Exception as e:
        print(f"Detection error: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/detection/all', methods=['GET'])
@jwt_required()
def get_all_detections_route():
    """Get all detection records"""
    try:
        detections = get_all_detections()
        return jsonify(detections), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/detection/<int:detection_id>', methods=['GET'])
@jwt_required()
def get_detection_by_id(detection_id):
    """Get specific detection"""
    try:
        detection = get_detection(detection_id)
        if not detection:
            return jsonify({'message': 'Detection not found'}), 404
        return jsonify(detection), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# ENCROACHMENT ROUTES
# ============================================================================

@app.route('/api/encroachment/all', methods=['GET'])
@jwt_required()
def get_all_encroachments_route():
    """Get all encroachment records"""
    try:
        encroachments = get_all_encroachments()
        return jsonify(encroachments), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/encroachment/pending', methods=['GET'])
@jwt_required()
def get_pending_encroachments_route():
    """Get encroachments pending review"""
    try:
        pending = get_pending_encroachments()
        return jsonify(pending), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/encroachment/<int:encroachment_id>', methods=['GET'])
@jwt_required()
def get_encroachment_by_id(encroachment_id):
    """Get specific encroachment"""
    try:
        encroachment = get_encroachment(encroachment_id)
        if not encroachment:
            return jsonify({'message': 'Encroachment not found'}), 404
        return jsonify(encroachment), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# ADMIN REVIEW ROUTES (MODULE 5)
# ============================================================================

@app.route('/api/admin/review/pending', methods=['GET'])
@jwt_required()
def admin_get_pending():
    """
    Get all cases pending admin review
    Sorted by priority (high severity first)
    """
    try:
        pending = admin_reviewer.get_pending_reviews()
        return jsonify(pending), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/review/<int:encroachment_id>', methods=['GET'])
@jwt_required()
def admin_get_review_details(encroachment_id):
    """Get detailed information for review"""
    try:
        details = admin_reviewer.get_review_details(encroachment_id)
        if not details:
            return jsonify({'message': 'Encroachment not found'}), 404
        return jsonify(details), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/review/<int:encroachment_id>/approve', methods=['POST'])
@jwt_required()
def admin_approve(encroachment_id):
    """
    Approve/confirm an encroachment
    
    Request body:
        {
            "remarks": "Optional admin notes"
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.json or {}
        remarks = data.get('remarks')
        
        success = admin_reviewer.approve_encroachment(
            encroachment_id, 
            user_id, 
            remarks
        )
        
        if success:
            return jsonify({'message': 'Encroachment approved'}), 200
        else:
            return jsonify({'message': 'Failed to approve'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/review/<int:encroachment_id>/reject', methods=['POST'])
@jwt_required()
def admin_reject(encroachment_id):
    """
    Reject/mark as false positive
    
    Request body:
        {
            "remarks": "Reason for rejection (required)"
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data or not data.get('remarks'):
            return jsonify({'message': 'Remarks required for rejection'}), 400
        
        success = admin_reviewer.reject_encroachment(
            encroachment_id,
            user_id,
            data['remarks']
        )
        
        if success:
            return jsonify({'message': 'Marked as false positive'}), 200
        else:
            return jsonify({'message': 'Failed to reject'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/review/<int:encroachment_id>/site-visit', methods=['POST'])
@jwt_required()
def admin_request_site_visit(encroachment_id):
    """
    Request physical site inspection
    
    Request body:
        {
            "remarks": "Details about site visit"
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.json or {}
        remarks = data.get('remarks')
        
        success = admin_reviewer.request_site_visit(
            encroachment_id,
            user_id,
            remarks
        )
        
        if success:
            return jsonify({'message': 'Site visit requested'}), 200
        else:
            return jsonify({'message': 'Failed to request site visit'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/review/<int:encroachment_id>/note', methods=['POST'])
@jwt_required()
def admin_add_note(encroachment_id):
    """
    Add a note without changing status
    
    Request body:
        {
            "note": "Note text"
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data or not data.get('note'):
            return jsonify({'message': 'Note text required'}), 400
        
        success = admin_reviewer.add_review_note(
            encroachment_id,
            user_id,
            data['note']
        )
        
        if success:
            return jsonify({'message': 'Note added'}), 200
        else:
            return jsonify({'message': 'Failed to add note'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/statistics', methods=['GET'])
@jwt_required()
def admin_get_statistics():
    """Get verification statistics"""
    try:
        stats = admin_reviewer.get_verification_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/priority-cases', methods=['GET'])
@jwt_required()
def admin_get_priority_cases():
    """Get high-priority cases needing urgent review"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        cases = admin_reviewer.get_high_priority_cases(limit)
        return jsonify(cases), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# REPORTING ROUTES (MODULE 4)
# ============================================================================

@app.route('/api/reports/generate/<int:detection_id>', methods=['POST'])
@jwt_required()
def generate_report(detection_id):
    """
    Generate reports for a detection
    
    Request body:
        {
            "format": "pdf" | "csv" | "txt" | "all"
        }
    """
    try:
        data = request.json or {}
        report_format = data.get('format', 'pdf')
        
        # Get detection
        detection = get_detection(detection_id)
        if not detection:
            return jsonify({'message': 'Detection not found'}), 404
        
        # Get image info
        image = get_image(detection['image_id'])
        
        # Get encroachments for this detection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM encroachments 
            WHERE detection_id = ? AND is_encroachment = 1
        ''', (detection_id,))
        encroachments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Prepare detection result
        detection_result = {
            'num_buildings': detection['num_buildings'],
            'total_area': detection['total_area']
        }
        
        # Prepare encroachment result
        encroachment_result = {
            'total_encroachments': len(encroachments),
            'encroachments': encroachments,
            'summary': {
                'severity_breakdown': {
                    'high': sum(1 for e in encroachments if e.get('severity') == 'high'),
                    'medium': sum(1 for e in encroachments if e.get('severity') == 'medium'),
                    'low': sum(1 for e in encroachments if e.get('severity') == 'low')
                },
                'affected_zones': list(set(e.get('zone_name') for e in encroachments))
            }
        }
        
        # Generate report(s)
        if report_format == 'all':
            reports = report_generator.generate_all_reports(
                image, detection_result, encroachment_result
            )
            return jsonify({
                'message': 'Reports generated',
                'reports': reports
            }), 200
        elif report_format == 'pdf':
            path = report_generator.generate_pdf_report(
                image, detection_result, encroachment_result
            )
        elif report_format == 'csv':
            path = report_generator.generate_csv_report(
                image, detection_result, encroachment_result
            )
        else:  # txt
            path = report_generator.generate_text_summary(
                image, detection_result, encroachment_result
            )
        
        return jsonify({
            'message': 'Report generated',
            'report_path': path,
            'format': report_format
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/reports/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_report(filename):
    """Download a generated report"""
    try:
        filepath = os.path.join(Config.REPORTS_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'message': 'Report not found'}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# STATISTICS ROUTES
# ============================================================================

@app.route('/api/statistics', methods=['GET'])
@jwt_required()
def get_statistics_route():
    """Get overall system statistics"""
    try:
        stats = get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@app.route('/api/encroachment/statistics', methods=['GET'])
@jwt_required()
def get_encroachment_statistics():
    """Get encroachment-specific statistics"""
    try:
        stats = get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'database': 'OK',
            'detection': 'OK',
            'encroachment': 'OK',
            'reporting': 'OK',
            'admin_review': 'OK'
        }
    }), 200


@app.route('/api/config/zones', methods=['GET'])
@jwt_required()
def get_public_zones():
    """Get configured public zones"""
    try:
        return jsonify(Config.PUBLIC_ZONES), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 ENCROACHMENT DETECTION BACKEND - STARTING")
    print("="*70)
    
    # Initialize database if needed
    from database import initialize_database
    if not os.path.exists('database.db'):
        print("\nDatabase not found. Initializing...")
        initialize_database()
    
    print("\n✅ All modules loaded successfully!")
    print("\nServer Information:")
    print(f"  URL: http://localhost:5000")
    print(f"  API Base: http://localhost:5000/api")
    print(f"  Health Check: http://localhost:5000/api/health")
    
    print("\nDefault Login:")
    print(f"  Email: {Config.DEFAULT_ADMIN_EMAIL}")
    print(f"  Password: {Config.DEFAULT_ADMIN_PASSWORD}")
    
    print("\nModules Active:")
    print("  ✓ Module 1: Database (SQLite)")
    print("  ✓ Module 2: Building Detection (OpenCV)")
    print("  ✓ Module 3: Encroachment Checking")
    print("  ✓ Module 4: Reporting (PDF/CSV)")
    print("  ✓ Module 5: Admin Review & Verification")
    
    print("\n" + "="*70)
    print("Press CTRL+C to stop the server")
    print("="*70 + "\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

