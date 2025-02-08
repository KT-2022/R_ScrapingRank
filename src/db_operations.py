import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
DB_PATH = os.path.join(DB_DIR, "items.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            shop_id TEXT,
            item_id TEXT,
            item_name TEXT,
            PRIMARY KEY (shop_id, item_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_item_to_db(shop_id, item_id, item_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (shop_id, item_id, item_name)
        VALUES (?, ?, ?)
    ''', (shop_id, item_id, item_name))
    conn.commit()
    conn.close()

def load_item_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT shop_id, item_id, item_name FROM items')
    item_ids = cursor.fetchall()
    conn.close()
    return item_ids

def delete_item_from_db(shop_id, item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE shop_id = ? AND item_id = ?', (shop_id, item_id))
    conn.commit()
    conn.close()
