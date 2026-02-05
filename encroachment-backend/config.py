"""
CONFIGURATION FILE
All settings for the application in one place
"""

import os

class Config:
    """Application configuration settings"""
    
    # Flask Settings
    SECRET_KEY = 'your-secret-key-change-in-production'
    
    # JWT Settings (for user authentication)
    JWT_SECRET_KEY = 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds
    
    # File Upload Settings
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'}
    
    # Detection Settings (OpenCV thresholds)
    EDGE_DETECTION_THRESHOLD_LOW = 50
    EDGE_DETECTION_THRESHOLD_HIGH = 150
    MIN_BUILDING_AREA = 500  # Minimum area in pixels to be considered a building
    
    # Encroachment Settings
    OVERLAP_THRESHOLD = 10  # Percentage - if building overlaps >10% with public zone, flag it
    
    # Public Zones (Simple coordinate-based system)
    # Format: (name, min_x, min_y, max_x, max_y)
    PUBLIC_ZONES = [
        {
            'name': 'Public Park Zone A',
            'type': 'park',
            'coordinates': (100, 100, 500, 500)  # Rectangle coordinates
        },
        {
            'name': 'Government Reserve Zone',
            'type': 'government',
            'coordinates': (600, 100, 1000, 500)
        },
        {
            'name': 'Road Reserve',
            'type': 'road',
            'coordinates': (100, 600, 500, 800)
        }
    ]
    
    # Report Settings
    REPORTS_FOLDER = 'reports'
    REPORT_LOGO_PATH = 'static/logo.png'  # Optional logo for PDF reports
    
    # Admin Settings
    DEFAULT_ADMIN_EMAIL = 'admin@example.com'
    DEFAULT_ADMIN_PASSWORD = 'admin123'
