import sqlite3
from datetime import datetime

DB_PATH = "../data/notes.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table des documents importés
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT,
        chemin_fichier TEXT,
        date_import TEXT,
        autres_tags TEXT
    )
    """)

    # Table des pages OCR extraites
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ocr_page (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        page_number INTEGER,
        text TEXT,
        FOREIGN KEY (document_id) REFERENCES document(id)
    )
    """)

    # Table des chunks textuels
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        start_offset INTEGER,
        text TEXT,
        FOREIGN KEY (document_id) REFERENCES document(id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    create_tables()
