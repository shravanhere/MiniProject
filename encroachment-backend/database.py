"""
DATABASE MODULE - SQLite Implementation
This file handles all database operations for the encroachment detection system.

WHAT IS SQLITE?
- SQLite is a simple file-based database (no server needed!)
- Perfect for small projects and learning
- Stores everything in a single file: database.db

TABLES WE'LL CREATE:
1. users - Store user accounts
2. images - Store uploaded image information
3. detections - Store building detection results
4. encroachments - Store flagged encroachments
"""

import sqlite3
from datetime import datetime
import os

# Database file name
DATABASE_FILE = 'database.db'


# ============================================================================
# PART 1: DATABASE CONNECTION
# ============================================================================

def get_db_connection():
    """
    Opens a connection to the SQLite database.
    
    HOW IT WORKS:
    - sqlite3.connect() opens the database file
    - If file doesn't exist, it creates a new one
    - Returns a connection object you can use to run SQL commands
    
    RETURNS:
        connection object
    """
    conn = sqlite3.connect(DATABASE_FILE)
    # This makes rows behave like dictionaries (easier to use!)
    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection(conn):
    """
    Closes the database connection.
    
    WHY CLOSE?
    - Saves changes to disk
    - Releases memory
    - Good practice to close when done
    """
    if conn:
        conn.close()


# ============================================================================
# PART 2: CREATE TABLES
# ============================================================================

def create_tables():
    """
    Creates all the tables we need in the database.
    
    WHAT ARE TABLES?
    - Tables are like Excel spreadsheets
    - Each table has columns (fields) and rows (records)
    - Example: users table has columns: id, name, email, password
    
    This function only needs to run ONCE to set up the database.
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("📊 Creating database tables...")
    
    # -------------------------------------------------------------------------
    # TABLE 1: USERS
    # -------------------------------------------------------------------------
    # Stores user accounts for login
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✓ Users table created")
    
    # EXPLANATION:
    # - id: Unique number for each user (auto-increments: 1, 2, 3...)
    # - name: User's full name
    # - email: User's email (UNIQUE = no duplicates allowed)
    # - password: User's password (we'll hash this later)
    # - role: 'admin' or 'user'
    # - created_at: When account was created (automatic)
    
    # -------------------------------------------------------------------------
    # TABLE 2: IMAGES
    # -------------------------------------------------------------------------
    # Stores information about uploaded images
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            image_type TEXT NOT NULL,
            location TEXT,
            latitude REAL,
            longitude REAL,
            upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            processed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("  ✓ Images table created")
    
    # EXPLANATION:
    # - id: Unique ID for each image
    # - filename: Name of the file (e.g., "satellite_001.jpg")
    # - filepath: Where the file is stored on disk
    # - image_type: 'satellite', 'drone', 'cctv', or 'mobile'
    # - location: Text description (e.g., "Sector 21, Block A")
    # - latitude/longitude: GPS coordinates (REAL = decimal numbers)
    # - upload_date: When image was uploaded
    # - user_id: Which user uploaded it (links to users table)
    # - processed: 0 = not processed yet, 1 = processed
    
    # -------------------------------------------------------------------------
    # TABLE 3: DETECTIONS
    # -------------------------------------------------------------------------
    # Stores building detection results
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            num_buildings INTEGER DEFAULT 0,
            total_area REAL DEFAULT 0,
            detection_data TEXT,
            mask_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE
        )
    ''')
    print("  ✓ Detections table created")
    
    # EXPLANATION:
    # - id: Unique ID for each detection
    # - image_id: Which image was analyzed (links to images table)
    # - num_buildings: How many buildings were found
    # - total_area: Total area of detected buildings (in pixels)
    # - detection_data: JSON string with detailed building info
    # - mask_path: Path to the detection mask image
    # - created_at: When detection was performed
    # - ON DELETE CASCADE: If image is deleted, delete its detections too
    
    # -------------------------------------------------------------------------
    # TABLE 4: ENCROACHMENTS
    # -------------------------------------------------------------------------
    # Stores flagged encroachments
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS encroachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id INTEGER NOT NULL,
            building_id INTEGER NOT NULL,
            is_encroachment INTEGER DEFAULT 0,
            overlap_percentage REAL DEFAULT 0,
            zone_name TEXT,
            severity TEXT DEFAULT 'low',
            status TEXT DEFAULT 'pending',
            remarks TEXT,
            verified_by INTEGER,
            verified_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (detection_id) REFERENCES detections (id) ON DELETE CASCADE,
            FOREIGN KEY (verified_by) REFERENCES users (id)
        )
    ''')
    print("  ✓ Encroachments table created")
    
    # EXPLANATION:
    # - id: Unique ID for each encroachment record
    # - detection_id: Which detection this belongs to
    # - building_id: Which building from the detection
    # - is_encroachment: 0 = not encroachment, 1 = is encroachment
    # - overlap_percentage: How much building overlaps public land
    # - zone_name: Name of the public zone (e.g., "Park Zone A")
    # - severity: 'low', 'medium', 'high'
    # - status: 'pending', 'confirmed', 'false_positive'
    # - remarks: Admin notes
    # - verified_by: Which admin verified it
    # - verified_at: When it was verified
    # - created_at: When encroachment was detected
    
    # Save all changes
    conn.commit()
    conn.close()
    
    print("✅ All tables created successfully!\n")


# ============================================================================
# PART 3: SAMPLE DATA (FOR TESTING)
# ============================================================================

def create_sample_data():
    """
    Creates a sample admin user for testing.
    You can login with: admin@example.com / admin123
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", ('admin@example.com',))
    if cursor.fetchone():
        print("⚠️  Admin user already exists")
        conn.close()
        return
    
    # Create admin user
    # NOTE: In production, you should hash passwords!
    # For simplicity, we're storing plain text (NOT RECOMMENDED for real apps)
    cursor.execute('''
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    ''', ('Admin User', 'admin@example.com', 'admin123', 'admin'))
    
    conn.commit()
    conn.close()
    
    print("✅ Sample admin user created!")
    print("   Email: admin@example.com")
    print("   Password: admin123\n")


# ============================================================================
# PART 4: HELPER FUNCTIONS (CRUD OPERATIONS)
# ============================================================================

# CRUD = Create, Read, Update, Delete (basic database operations)

# -------------------------------------------------------------------------
# USER OPERATIONS
# -------------------------------------------------------------------------

def create_user(name, email, password, role='user'):
    """
    Creates a new user account.
    
    EXAMPLE:
        create_user('John Doe', 'john@example.com', 'password123')
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password, role))
        
        conn.commit()
        user_id = cursor.lastrowid  # Gets the ID of newly created user
        conn.close()
        
        return {'success': True, 'user_id': user_id}
    
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': 'Email already exists'}


def get_user_by_email(email):
    """
    Finds a user by their email address.
    
    RETURNS:
        Dictionary with user data, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return dict(user)  # Convert to dictionary
    return None


def get_user_by_id(user_id):
    """
    Finds a user by their ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return dict(user)
    return None


# -------------------------------------------------------------------------
# IMAGE OPERATIONS
# -------------------------------------------------------------------------

def create_image(filename, filepath, image_type, user_id, location=None, latitude=None, longitude=None):
    """
    Saves image information to database.
    
    EXAMPLE:
        create_image(
            'satellite_001.jpg',
            '/uploads/satellite_001.jpg',
            'satellite',
            1,
            'Sector 21',
            12.9716,
            77.5946
        )
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO images (filename, filepath, image_type, user_id, location, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, filepath, image_type, user_id, location, latitude, longitude))
    
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    
    return image_id


def get_image(image_id):
    """
    Gets image information by ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM images WHERE id = ?', (image_id,))
    image = cursor.fetchone()
    
    conn.close()
    
    if image:
        return dict(image)
    return None


def get_all_images():
    """
    Gets all uploaded images.
    
    RETURNS:
        List of dictionaries, each containing image data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM images ORDER BY upload_date DESC')
    images = cursor.fetchall()
    
    conn.close()
    
    return [dict(img) for img in images]


def update_image_processed(image_id):
    """
    Marks an image as processed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE images SET processed = 1 WHERE id = ?', (image_id,))
    
    conn.commit()
    conn.close()


def delete_image(image_id):
    """
    Deletes an image record.
    (Detections and encroachments will be auto-deleted due to CASCADE)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
    
    conn.commit()
    conn.close()


# -------------------------------------------------------------------------
# DETECTION OPERATIONS
# -------------------------------------------------------------------------

def create_detection(image_id, num_buildings, total_area, detection_data=None, mask_path=None):
    """
    Saves building detection results.
    
    EXAMPLE:
        create_detection(
            image_id=1,
            num_buildings=5,
            total_area=25000,
            detection_data='{"buildings": [...]}',
            mask_path='/uploads/masks/mask_001.png'
        )
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO detections (image_id, num_buildings, total_area, detection_data, mask_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (image_id, num_buildings, total_area, detection_data, mask_path))
    
    conn.commit()
    detection_id = cursor.lastrowid
    conn.close()
    
    return detection_id


def get_detection(detection_id):
    """
    Gets detection results by ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM detections WHERE id = ?', (detection_id,))
    detection = cursor.fetchone()
    
    conn.close()
    
    if detection:
        return dict(detection)
    return None


def get_detections_by_image(image_id):
    """
    Gets all detections for a specific image.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM detections WHERE image_id = ?', (image_id,))
    detections = cursor.fetchall()
    
    conn.close()
    
    return [dict(d) for d in detections]


def get_all_detections():
    """
    Gets all detection records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM detections ORDER BY created_at DESC')
    detections = cursor.fetchall()
    
    conn.close()
    
    return [dict(d) for d in detections]


# -------------------------------------------------------------------------
# ENCROACHMENT OPERATIONS
# -------------------------------------------------------------------------

def create_encroachment(detection_id, building_id, is_encroachment, overlap_percentage, 
                       zone_name=None, severity='low'):
    """
    Records an encroachment.
    
    EXAMPLE:
        create_encroachment(
            detection_id=1,
            building_id=3,
            is_encroachment=1,
            overlap_percentage=45.5,
            zone_name='Public Park Zone',
            severity='high'
        )
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO encroachments 
        (detection_id, building_id, is_encroachment, overlap_percentage, zone_name, severity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (detection_id, building_id, is_encroachment, overlap_percentage, zone_name, severity))
    
    conn.commit()
    encroachment_id = cursor.lastrowid
    conn.close()
    
    return encroachment_id


def get_encroachment(encroachment_id):
    """
    Gets encroachment by ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM encroachments WHERE id = ?', (encroachment_id,))
    encroachment = cursor.fetchone()
    
    conn.close()
    
    if encroachment:
        return dict(encroachment)
    return None


def get_all_encroachments():
    """
    Gets all encroachment records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM encroachments ORDER BY created_at DESC')
    encroachments = cursor.fetchall()
    
    conn.close()
    
    return [dict(e) for e in encroachments]


def get_pending_encroachments():
    """
    Gets all encroachments that need verification.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM encroachments 
        WHERE status = 'pending' AND is_encroachment = 1
        ORDER BY severity DESC, created_at DESC
    ''')
    encroachments = cursor.fetchall()
    
    conn.close()
    
    return [dict(e) for e in encroachments]


def verify_encroachment(encroachment_id, user_id, status, remarks=None):
    """
    Admin verifies an encroachment.
    
    EXAMPLE:
        verify_encroachment(
            encroachment_id=5,
            user_id=1,
            status='confirmed',
            remarks='Verified through site visit'
        )
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE encroachments
        SET status = ?, remarks = ?, verified_by = ?, verified_at = ?
        WHERE id = ?
    ''', (status, remarks, user_id, datetime.now().isoformat(), encroachment_id))
    
    conn.commit()
    conn.close()


# -------------------------------------------------------------------------
# STATISTICS FUNCTIONS
# -------------------------------------------------------------------------

def get_statistics():
    """
    Gets overall system statistics.
    
    RETURNS:
        Dictionary with counts and stats
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count total images
    cursor.execute('SELECT COUNT(*) as count FROM images')
    total_images = cursor.fetchone()['count']
    
    # Count total detections
    cursor.execute('SELECT COUNT(*) as count FROM detections')
    total_detections = cursor.fetchone()['count']
    
    # Count encroachments
    cursor.execute('SELECT COUNT(*) as count FROM encroachments WHERE is_encroachment = 1')
    total_encroachments = cursor.fetchone()['count']
    
    # Count pending encroachments
    cursor.execute('SELECT COUNT(*) as count FROM encroachments WHERE status = "pending" AND is_encroachment = 1')
    pending_encroachments = cursor.fetchone()['count']
    
    # Count confirmed encroachments
    cursor.execute('SELECT COUNT(*) as count FROM encroachments WHERE status = "confirmed"')
    confirmed_encroachments = cursor.fetchone()['count']
    
    # Count false positives
    cursor.execute('SELECT COUNT(*) as count FROM encroachments WHERE status = "false_positive"')
    false_positives = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_images': total_images,
        'total_detections': total_detections,
        'total_encroachments': total_encroachments,
        'pending_review': pending_encroachments,
        'confirmed': confirmed_encroachments,
        'false_positives': false_positives
    }


# ============================================================================
# PART 5: INITIALIZATION
# ============================================================================

def initialize_database():
    """
    Sets up the complete database.
    Run this once when starting the project!
    """
    print("\n" + "="*60)
    print("🗄️  INITIALIZING DATABASE")
    print("="*60 + "\n")
    
    # Check if database already exists
    if os.path.exists(DATABASE_FILE):
        print(f"⚠️  Database file '{DATABASE_FILE}' already exists")
        response = input("   Do you want to recreate it? (yes/no): ")
        if response.lower() != 'yes':
            print("   Keeping existing database.\n")
            return
        else:
            os.remove(DATABASE_FILE)
            print("   Deleted old database.\n")
    
    # Create tables
    create_tables()
    
    # Add sample data
    create_sample_data()
    
    print("="*60)
    print("✅ DATABASE READY TO USE!")
    print("="*60)
    print("\nYou can now:")
    print("  1. Login with admin@example.com / admin123")
    print("  2. Upload images")
    print("  3. Run detections")
    print("  4. Check encroachments\n")


# ============================================================================
# PART 6: TESTING FUNCTIONS
# ============================================================================

def test_database():
    """
    Tests all database functions to make sure everything works.
    """
    print("\n" + "="*60)
    print("🧪 TESTING DATABASE FUNCTIONS")
    print("="*60 + "\n")
    
    # Test 1: Get admin user
    print("Test 1: Get admin user...")
    user = get_user_by_email('admin@example.com')
    if user:
        print(f"  ✓ Found user: {user['name']}")
    else:
        print("  ✗ User not found!")
    
    # Test 2: Create image
    print("\nTest 2: Create image record...")
    image_id = create_image(
        'test_satellite.jpg',
        '/uploads/test_satellite.jpg',
        'satellite',
        user['id'],
        'Test Location',
        12.9716,
        77.5946
    )
    print(f"  ✓ Image created with ID: {image_id}")
    
    # Test 3: Get image
    print("\nTest 3: Retrieve image...")
    image = get_image(image_id)
    print(f"  ✓ Retrieved image: {image['filename']}")
    
    # Test 4: Create detection
    print("\nTest 4: Create detection record...")
    detection_id = create_detection(
        image_id=image_id,
        num_buildings=3,
        total_area=15000
    )
    print(f"  ✓ Detection created with ID: {detection_id}")
    
    # Test 5: Create encroachment
    print("\nTest 5: Create encroachment record...")
    encroachment_id = create_encroachment(
        detection_id=detection_id,
        building_id=1,
        is_encroachment=1,
        overlap_percentage=35.5,
        zone_name='Test Public Zone',
        severity='medium'
    )
    print(f"  ✓ Encroachment created with ID: {encroachment_id}")
    
    # Test 6: Get statistics
    print("\nTest 6: Get statistics...")
    stats = get_statistics()
    print(f"  ✓ Total images: {stats['total_images']}")
    print(f"  ✓ Total detections: {stats['total_detections']}")
    print(f"  ✓ Total encroachments: {stats['total_encroachments']}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")


# ============================================================================
# MAIN - RUN THIS FILE DIRECTLY TO INITIALIZE DATABASE
# ============================================================================

if __name__ == '__main__':
    """
    When you run: python database.py
    This code will execute
    """
    
    # Initialize database
    initialize_database()
    
    # Run tests
    test_database()
    
    print("\n✅ Database is ready! You can now start your Flask app.\n")
