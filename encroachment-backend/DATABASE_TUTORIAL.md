# 🗄️ SQLITE DATABASE - COMPLETE BEGINNER'S TUTORIAL

## 📚 Table of Contents
1. [What is SQLite?](#what-is-sqlite)
2. [Understanding Tables](#understanding-tables)
3. [Database Structure](#database-structure)
4. [How to Use](#how-to-use)
5. [Common Operations](#common-operations)
6. [Troubleshooting](#troubleshooting)

---

## 🤔 What is SQLite?

### Simple Explanation:
**SQLite is like an Excel file for storing data, but much more powerful!**

### Key Features:
- ✅ **No server needed** - Just a single file (`database.db`)
- ✅ **Built into Python** - No extra installation
- ✅ **Perfect for learning** - Easy to understand
- ✅ **Great for small projects** - Like your college project!

### Comparison:

| Feature | Excel | SQLite |
|---------|-------|--------|
| File Type | .xlsx | .db |
| Tables | Sheets | Tables |
| Rows | Rows | Records |
| Columns | Columns | Fields |
| Speed | Slow for large data | Fast |
| Relationships | Manual | Automatic (Foreign Keys) |

---

## 📊 Understanding Tables

### What is a Table?
A table is like a spreadsheet with columns and rows.

**Example: USERS table**

| id | name       | email              | password | role  |
|----|------------|-------------------|----------|-------|
| 1  | Admin User | admin@example.com | admin123 | admin |
| 2  | John Doe   | john@example.com  | pass456  | user  |
| 3  | Jane Smith | jane@example.com  | pass789  | user  |

### Table Terminology:

```
┌─────────────────────────────────────┐
│          USERS TABLE                │
├─────┬───────────┬─────────────┬────┤
│ id  │   name    │    email    │... │  ← COLUMNS (Fields)
├─────┼───────────┼─────────────┼────┤
│  1  │ Admin     │ admin@...   │... │  ← ROW 1 (Record)
│  2  │ John      │ john@...    │... │  ← ROW 2 (Record)
│  3  │ Jane      │ jane@...    │... │  ← ROW 3 (Record)
└─────┴───────────┴─────────────┴────┘
       ↑
     PRIMARY KEY (Unique ID)
```

---

## 🏗️ Database Structure

### Our 4 Tables:

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  DATABASE: encroachment_detection                   │
│                                                      │
│  ┌───────────┐     ┌──────────┐                    │
│  │  USERS    │────→│  IMAGES  │                    │
│  └───────────┘     └──────────┘                    │
│       user_id            │                          │
│                          ↓                          │
│                   ┌──────────────┐                 │
│                   │  DETECTIONS  │                 │
│                   └──────────────┘                 │
│                          │                          │
│                          ↓                          │
│                   ┌───────────────┐                │
│                   │ ENCROACHMENTS │                │
│                   └───────────────┘                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Table Relationships:

1. **USERS → IMAGES**: One user can upload many images
2. **IMAGES → DETECTIONS**: One image can have many detection results
3. **DETECTIONS → ENCROACHMENTS**: One detection can have many encroachments

---

## 📋 Detailed Table Structures

### TABLE 1: USERS
**Purpose:** Store user accounts

| Column     | Type    | Description              | Example           |
|------------|---------|--------------------------|-------------------|
| id         | INTEGER | Unique user ID           | 1                 |
| name       | TEXT    | User's full name         | "Admin User"      |
| email      | TEXT    | Email (login username)   | "admin@ex.com"    |
| password   | TEXT    | Password (plain text)    | "admin123"        |
| role       | TEXT    | 'admin' or 'user'        | "admin"           |
| created_at | TEXT    | Account creation date    | "2026-02-01..."   |

**SQL to create:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### TABLE 2: IMAGES
**Purpose:** Store uploaded image information

| Column      | Type    | Description                    | Example                |
|-------------|---------|--------------------------------|------------------------|
| id          | INTEGER | Unique image ID                | 1                      |
| filename    | TEXT    | Image file name                | "satellite_001.jpg"    |
| filepath    | TEXT    | Where file is stored           | "/uploads/sat_001.jpg" |
| image_type  | TEXT    | satellite/drone/cctv/mobile    | "satellite"            |
| location    | TEXT    | Location description           | "Sector 21, Block A"   |
| latitude    | REAL    | GPS latitude                   | 12.9716                |
| longitude   | REAL    | GPS longitude                  | 77.5946                |
| upload_date | TEXT    | When uploaded                  | "2026-02-01..."        |
| user_id     | INTEGER | Who uploaded (links to users)  | 1                      |
| processed   | INTEGER | 0=not processed, 1=processed   | 1                      |

**SQL to create:**
```sql
CREATE TABLE images (
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
```

### TABLE 3: DETECTIONS
**Purpose:** Store building detection results

| Column         | Type    | Description                      | Example              |
|----------------|---------|----------------------------------|----------------------|
| id             | INTEGER | Unique detection ID              | 1                    |
| image_id       | INTEGER | Which image (links to images)    | 1                    |
| num_buildings  | INTEGER | How many buildings found         | 5                    |
| total_area     | REAL    | Total area in pixels             | 25000                |
| detection_data | TEXT    | JSON with building details       | "{buildings: [...]}" |
| mask_path      | TEXT    | Path to detection mask image     | "/masks/mask_1.png"  |
| created_at     | TEXT    | When detection was run           | "2026-02-01..."      |

**SQL to create:**
```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    num_buildings INTEGER DEFAULT 0,
    total_area REAL DEFAULT 0,
    detection_data TEXT,
    mask_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE
)
```

### TABLE 4: ENCROACHMENTS
**Purpose:** Store flagged encroachments

| Column             | Type    | Description                     | Example               |
|--------------------|---------|--------------------------------|-----------------------|
| id                 | INTEGER | Unique encroachment ID         | 1                     |
| detection_id       | INTEGER | Which detection                | 1                     |
| building_id        | INTEGER | Which building from detection  | 3                     |
| is_encroachment    | INTEGER | 0=no, 1=yes                   | 1                     |
| overlap_percentage | REAL    | How much overlap              | 45.5                  |
| zone_name          | TEXT    | Public zone name              | "Public Park Zone A"  |
| severity           | TEXT    | low/medium/high               | "high"                |
| status             | TEXT    | pending/confirmed/false       | "pending"             |
| remarks            | TEXT    | Admin notes                   | "Verified on site"    |
| verified_by        | INTEGER | Which admin verified          | 1                     |
| verified_at        | TEXT    | When verified                 | "2026-02-01..."       |
| created_at         | TEXT    | When detected                 | "2026-02-01..."       |

**SQL to create:**
```sql
CREATE TABLE encroachments (
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
```

---

## 🚀 How to Use

### STEP 1: Initialize Database

```bash
# Run the database script
python database.py
```

**What happens:**
1. Creates `database.db` file
2. Creates all 4 tables
3. Creates admin user
4. Runs tests

**Expected output:**
```
📊 Creating database tables...
  ✓ Users table created
  ✓ Images table created
  ✓ Detections table created
  ✓ Encroachments table created
✅ Sample admin user created!
```

### STEP 2: View Database (Optional)

**Option A: Using Python**
```python
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# See all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())

conn.close()
```

**Option B: Using DB Browser (Download)**
- Download: https://sqlitebrowser.org/
- Open `database.db`
- See tables visually!

### STEP 3: Use in Your Code

```python
from database import *

# Example 1: Create a new user
result = create_user('John Doe', 'john@example.com', 'password123')
print(f"User created with ID: {result['user_id']}")

# Example 2: Get user by email
user = get_user_by_email('admin@example.com')
print(f"Found user: {user['name']}")

# Example 3: Upload an image
image_id = create_image(
    filename='satellite_001.jpg',
    filepath='/uploads/satellite_001.jpg',
    image_type='satellite',
    user_id=1,
    location='Sector 21',
    latitude=12.9716,
    longitude=77.5946
)
print(f"Image saved with ID: {image_id}")

# Example 4: Save detection results
detection_id = create_detection(
    image_id=1,
    num_buildings=5,
    total_area=25000
)
print(f"Detection saved with ID: {detection_id}")

# Example 5: Flag an encroachment
encroachment_id = create_encroachment(
    detection_id=1,
    building_id=3,
    is_encroachment=1,
    overlap_percentage=45.5,
    zone_name='Public Park Zone',
    severity='high'
)
print(f"Encroachment flagged with ID: {encroachment_id}")

# Example 6: Get statistics
stats = get_statistics()
print(f"Total images: {stats['total_images']}")
print(f"Total encroachments: {stats['total_encroachments']}")
```

---

## 🔧 Common Operations

### CREATE (Insert Data)

```python
# Create a user
create_user('Alice', 'alice@example.com', 'pass123')

# Create an image record
create_image('drone_01.jpg', '/uploads/drone_01.jpg', 'drone', user_id=1)

# Create a detection
create_detection(image_id=1, num_buildings=3, total_area=15000)

# Create an encroachment
create_encroachment(detection_id=1, building_id=1, is_encroachment=1, 
                    overlap_percentage=30, severity='medium')
```

### READ (Get Data)

```python
# Get one user
user = get_user_by_email('admin@example.com')

# Get one image
image = get_image(1)

# Get all images
all_images = get_all_images()

# Get all detections
all_detections = get_all_detections()

# Get pending encroachments
pending = get_pending_encroachments()

# Get statistics
stats = get_statistics()
```

### UPDATE (Modify Data)

```python
# Mark image as processed
update_image_processed(image_id=1)

# Verify an encroachment
verify_encroachment(
    encroachment_id=1,
    user_id=1,
    status='confirmed',
    remarks='Verified through satellite imagery'
)
```

### DELETE (Remove Data)

```python
# Delete an image (will also delete its detections and encroachments)
delete_image(image_id=1)
```

---

## 🎯 Real-World Example: Complete Flow

```python
# 1. User logs in
user = get_user_by_email('admin@example.com')
if user and user['password'] == 'admin123':
    print("Login successful!")
    
    # 2. User uploads image
    image_id = create_image(
        'satellite_sector21.jpg',
        '/uploads/satellite_sector21.jpg',
        'satellite',
        user['id'],
        'Sector 21, Block A',
        12.9716,
        77.5946
    )
    print(f"Image uploaded: ID {image_id}")
    
    # 3. System runs detection
    detection_id = create_detection(
        image_id=image_id,
        num_buildings=7,
        total_area=35000,
        detection_data='{"buildings": [...]}'
    )
    print(f"Detection complete: Found 7 buildings")
    
    # 4. System checks for encroachment
    # Building 3 overlaps public park by 55%
    encroachment_id = create_encroachment(
        detection_id=detection_id,
        building_id=3,
        is_encroachment=1,
        overlap_percentage=55.0,
        zone_name='Municipal Park Zone A',
        severity='high'
    )
    print(f"Encroachment flagged! ID: {encroachment_id}")
    
    # 5. Admin verifies
    verify_encroachment(
        encroachment_id=encroachment_id,
        user_id=user['id'],
        status='confirmed',
        remarks='Site visit confirmed illegal construction'
    )
    print("Encroachment verified!")
    
    # 6. Get updated statistics
    stats = get_statistics()
    print(f"\nSystem Statistics:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Total detections: {stats['total_detections']}")
    print(f"  Confirmed encroachments: {stats['confirmed']}")
    print(f"  Pending review: {stats['pending_review']}")
```

**Output:**
```
Login successful!
Image uploaded: ID 1
Detection complete: Found 7 buildings
Encroachment flagged! ID 1
Encroachment verified!

System Statistics:
  Total images: 1
  Total detections: 1
  Confirmed encroachments: 1
  Pending review: 0
```

---

## 🐛 Troubleshooting

### Problem 1: "database is locked"
**Cause:** Another program has the database open
**Solution:**
```python
# Always close connections
conn = get_db_connection()
# ... do stuff ...
conn.close()  # Don't forget this!
```

### Problem 2: "no such table"
**Cause:** Tables not created yet
**Solution:**
```bash
python database.py  # Run initialization
```

### Problem 3: "UNIQUE constraint failed"
**Cause:** Trying to insert duplicate email
**Solution:**
```python
# Check if user exists first
existing_user = get_user_by_email('john@example.com')
if not existing_user:
    create_user('John', 'john@example.com', 'pass123')
```

### Problem 4: Can't see data
**Cause:** Need to commit changes
**Solution:**
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("INSERT INTO ...")
conn.commit()  # This saves the changes!
conn.close()
```

---

## 📚 Key SQL Concepts (Simplified)

### PRIMARY KEY
- **What:** Unique ID for each record
- **Why:** So you can find specific records
- **Example:** `id INTEGER PRIMARY KEY AUTOINCREMENT`

### FOREIGN KEY
- **What:** Links to another table's PRIMARY KEY
- **Why:** Creates relationships between tables
- **Example:** `user_id INTEGER REFERENCES users(id)`

### NOT NULL
- **What:** Field must have a value
- **Why:** Prevents empty required fields
- **Example:** `name TEXT NOT NULL`

### DEFAULT
- **What:** Automatic value if none provided
- **Why:** Saves typing, ensures consistency
- **Example:** `role TEXT DEFAULT 'user'`

### UNIQUE
- **What:** No two records can have same value
- **Why:** Prevents duplicates (like emails)
- **Example:** `email TEXT UNIQUE`

### CASCADE
- **What:** Auto-delete related records
- **Why:** Keeps database clean
- **Example:** `ON DELETE CASCADE`

---

## ✅ Summary

### What You Learned:
1. ✅ What SQLite is and how it works
2. ✅ How to create tables with proper structure
3. ✅ How to insert, read, update, and delete data
4. ✅ How tables relate to each other
5. ✅ How to use the database in your project

### What You Have Now:
1. ✅ Complete database file (`database.py`)
2. ✅ 4 tables for your project
3. ✅ All CRUD functions ready to use
4. ✅ Sample admin account
5. ✅ Testing functions

### Next Steps:
1. Run `python database.py` to initialize
2. Use the functions in your Flask app
3. Connect to your frontend
4. Start building features!

---

**🎉 You now understand SQLite databases!**

The `database.py` file has everything you need. Just import the functions and use them in your Flask app!

```python
from database import *

# Now you can use all the functions!
user = get_user_by_email('admin@example.com')
```
