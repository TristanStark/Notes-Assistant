import os
import base64
import sqlite3
from datetime import datetime
from openai import OpenAI

# Configuration
DB_PATH = "../data/notes.db"
INPUT_FOLDER = "../data/scans"
MODEL = "gpt-4.1-nano"  # ou "gpt-4-vision-preview"

# Initialise le client OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def gpt_ocr_image(image_path):
    print(f"🔍 GPT OCR sur : {image_path}")

    b64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un expert en transcription d'images manuscrites. "
                    "Tu dois transcrire fidèlement tout le texte présent sur l'image. "
                    "Écris la transcription en français, sans rien inventer ni résumer."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcris tout le texte manuscrit lisible sur cette image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ]
    )

    text = response.choices[0].message.content.strip()
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
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        path = os.path.join(INPUT_FOLDER, filename)
        titre = os.path.splitext(filename)[0]

        # OCR via GPT
        text = gpt_ocr_image(path)

        print(f"📜 Texte OCR =\n{text}\n{'-'*50}")

        # Insert document
        #doc_id = insert_document(conn, titre, path)

        # Insert OCR page (page_number = 1)
        #insert_ocr_page(conn, doc_id, 1, text)

        print(f"✅ Importé : {filename}")

    conn.close()
    print("✅ Tous les fichiers ont été traités.")

if __name__ == "__main__":
    process_folder()
