import sqlite3

DB_PATH = 'inventory.db'


def get_connection():
    return sqlite3.connect(DB_PATH)


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
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin', 'admin')
        )

    # 🔥 IMPORTANT CALLS
    seed_data(cursor)
    upgrade_schema(cursor)

    conn.commit()
    conn.close()


# 👤 REGISTER USER
def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
        (username, password)
    )

    conn.commit()
    conn.close()
    return True, "Registration successful."


# 🔐 LOGIN
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


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