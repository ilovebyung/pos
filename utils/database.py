import sqlite3

# Database connection
def get_db_connection():
    conn = sqlite3.connect('pos.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn
