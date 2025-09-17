import os
import sqlite3
from datetime import datetime
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DB_PATH = "../data/notes.db"
INPUT_FOLDER = "../data/scans"
LANG = "fra"  # ou "eng", "fra+eng" etc.

def ocr_image(path):
    """Fait l'OCR sur une image et renvoie le texte."""
    print(f"🔍 OCR sur : {path}")
    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang=LANG)
    return text

def insert_document(conn, titre, chemin):
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO document (titre, chemin_fichier, date_import) VALUES (?, ?, ?)",
        (titre, chemin, now)
    )
    conn.commit()
    return cursor.lastrowid

def insert_ocr_page(conn, document_id, page_number, text):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ocr_page (document_id, page_number, text) VALUES (?, ?, ?)",
        (document_id, page_number, text)
    )
    conn.commit()

def process_folder():
    conn = sqlite3.connect(DB_PATH)

    files = sorted(os.listdir(INPUT_FOLDER))
    for filename in files:
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff')):
            continue

        path = os.path.join(INPUT_FOLDER, filename)
        titre = os.path.splitext(filename)[0]

        # OCR
        text = ocr_image(path)
        if not text.strip():
            print(f"⚠️ Aucune donnée OCR pour : {filename}")
            continue
        print(f"📄 Titre : {titre}"
              f"\n📂 Chemin : {path}\n📝 Texte OCR : {text[:100]}...")
        
        # Insert document
        #doc_id = insert_document(conn, titre, path)

        # Insert OCR page (page_number = 1 car image unique)
        #insert_ocr_page(conn, doc_id, 1, text)

        print(f"✅ Importé : {filename}")

    conn.close()
    print("✅ Tous les fichiers ont été traités.")

if __name__ == "__main__":
    process_folder()
