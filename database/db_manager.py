import sqlite3
import hashlib


DB_PATH = 'inventory.db'


def get_connection():
    return sqlite3.connect(DB_PATH)


# 🔒 PASSWORD HASHING
def hash_password(password):
    """Securely hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# 🔥 AUTO SEED DATA
def seed_data(cursor):
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:

        print("Seeding initial inventory data...")

        sample_items = [
            (101, "Laptop Dell Inspiron 15", 12, 55000, "Electronics", "TechWorld Pvt Ltd"),
            (102, "Wireless Mouse Logitech M235", 50, 799, "Accessories", "GadgetHub"),
            (103, "Mechanical Keyboard Redragon K552", 30, 3499, "Accessories", "KeyTech"),
            (104, "24-inch Monitor Samsung LED", 20, 12999, "Electronics", "DisplayMart"),
            (105, "External Hard Drive 1TB Seagate", 25, 4200, "Storage", "Storage Solutions"),
            (106, "USB Flash Drive 64GB SanDisk", 100, 599, "Storage", "Storage Solutions"),
            (107, "Office Chair Ergonomic", 15, 7500, "Furniture", "Comfort Seating"),
            (108, "Study Desk Wooden", 10, 9999, "Furniture", "FurniCraft"),
            (109, "Printer HP LaserJet Pro", 8, 18500, "Electronics", "PrintTech"),
            (110, "Router TP-Link Dual Band", 18, 2299, "Networking", "NetConnect"),
            (111, "CCTV Camera 1080p Security Cam", 22, 3200, "Security", "SafeHome"),
            (112, "Power Bank 10000mAh Mi", 40, 1299, "Accessories", "GadgetHub"),
            (113, "Air Conditioner 1.5 Ton LG", 5, 38000, "Appliances", "CoolTech"),
            (114, "Water Dispenser", 7, 6800, "Appliances", "AquaPure"),
            (115, "Extension Board 6 Socket Anchor", 60, 450, "Electrical", "ElectroMart")
        ]

        cursor.executemany(
            "INSERT INTO items (id, name, stock, price, category, supplier) VALUES (?, ?, ?, ?, ?, ?)",
            sample_items
        )


# 🔧 SCHEMA UPGRADE (SAFE)
def upgrade_schema(cursor):
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]

    if "username" not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN username TEXT DEFAULT 'System'")


# 🚀 INIT DATABASE
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ ITEMS TABLE (FIXED: removed AUTOINCREMENT)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        stock INTEGER NOT NULL,
        price REAL NOT NULL,
        category TEXT,
        supplier TEXT
    )
    ''')

    # ✅ ORDERS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        quantity INTEGER,
        order_type TEXT,
        timestamp TEXT,
        username TEXT DEFAULT 'System',
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    ''')

    # ✅ USERS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    # ✅ CREATE ADMIN USER
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_admin_pass = hash_password('admin')
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', hashed_admin_pass, 'admin')
        )

    # 🔥 IMPORTANT CALLS
    seed_data(cursor)
    upgrade_schema(cursor)

    conn.commit()
    conn.close()


# 👤 REGISTER USER
def register_user(username, password):
    """
    Registers a new user. All new users default to the 'user' role.
    Role elevation must be done subsequently via an existing admin.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    hashed_pass = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
        (username, hashed_pass)
    )

    conn.commit()
    conn.close()
    return True, f"Successfully created user: {username}."
# ⬆️ PROMOTE USER TO ADMIN
def promote_to_admin(target_username, admin_username, admin_password):
    """
    Promote an existing user to admin. Requires current admin credentials.
    """
    # 1. Verify admin credentials
    creator = authenticate_user(admin_username, admin_password)
    if not creator or creator[3] != 'admin':
        return False, "Unauthorized: Invalid admin credentials."
        
    # Prevent self-modification
    if target_username == admin_username:
        return False, "Cannot modify your own role."

    conn = get_connection()
    cursor = conn.cursor()

    # 2. Verify target user exists and isn't already admin
    cursor.execute("SELECT role FROM users WHERE username=?", (target_username,))
    target_user = cursor.fetchone()
    
    if not target_user:
        conn.close()
        return False, f"User '{target_username}' does not exist."
        
    if target_user[0] == 'admin':
        conn.close()
        return False, f"User '{target_username}' is already an admin."

    # 3. Promote user
    cursor.execute(
        "UPDATE users SET role = 'admin' WHERE username=?",
        (target_username,)
    )
    # Optional: Log the promotion action here to an audit table
    
    conn.commit()
    conn.close()
    return True, f"Success: {target_username} is now an admin."


# 🔐 LOGIN
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, password, role FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        db_id, db_user, db_pass, db_role = user
        hashed_input = hash_password(password)

        # 1. Check if it matches the current hash
        if db_pass == hashed_input:
            return user
        
        # 2. Backward compatibility: check if it matches plain text
        if db_pass == password:
            # Upgrade this user to hashed password now
            execute_query("UPDATE users SET password=? WHERE id=?", (hashed_input, db_id))
            return user

    return None


# 👥 GET USERS
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users WHERE role != 'admin'")
    users = cursor.fetchall()

    conn.close()
    return users


# ❌ DELETE USER
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()


# ⚙️ GENERIC QUERY EXECUTOR
def execute_query(query, params=(), fetch=False, commit=True):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params)

    result = None
    if fetch:
        result = cursor.fetchall()

    if commit:
        conn.commit()

    last_row_id = cursor.lastrowid
    conn.close()

    return result if fetch else last_row_id