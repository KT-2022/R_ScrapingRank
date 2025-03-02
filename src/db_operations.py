import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "..","assets_binary", "db")
DB_PATH = os.path.join(DB_DIR, "items.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id TEXT,
            item_id TEXT,
            item_name TEXT,
            search_word TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_item_to_db(shop_id, item_id, item_name, search_word):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (shop_id, item_id, item_name, search_word)
        VALUES (?, ?, ?, ?)
    ''', (shop_id, item_id, item_name, search_word))
    conn.commit()
    conn.close()

def load_item_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, shop_id, item_id, item_name, search_word FROM items')
    item_ids = cursor.fetchall()
    conn.close()
    return item_ids

def delete_item_from_db(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
