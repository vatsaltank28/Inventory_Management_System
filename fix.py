import sqlite3
conn = sqlite3.connect('inventory.db')
conn.execute("UPDATE users SET password='28012007' WHERE username='admin'")
conn.commit()
conn.close()
print("Fixed admin password.")
