import sqlite3
import json
import os

# Paths
DB_PATH = 'ecommerce.db'
PRODUCTS_JSON = 'data/products.json'

# Connect to SQLite (creates file if not exists)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    image TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT NOT NULL,
    sender TEXT NOT NULL, -- 'user' or 'bot'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Import products from JSON
if os.path.exists(PRODUCTS_JSON):
    with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
        products = json.load(f)
    for product in products:
        # Handle products that might not have an image field
        image = product.get('image', None)
        c.execute('''
            INSERT OR IGNORE INTO products (id, name, price, image)
            VALUES (?, ?, ?, ?)
        ''', (product['id'], product['name'], product['price'], image))
    print(f"Imported {len(products)} products.")
else:
    print(f"{PRODUCTS_JSON} not found.")

conn.commit()
conn.close()
print("Database setup complete.") 