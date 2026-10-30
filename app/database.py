import sqlite3

from app.data import FAQS
DB_FILE = "faq.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS faqs (id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT NOT NULL DEFAULT '')
    """)

    # If the table is empty, fill it from data.py
    count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
    if count == 0:
        for faq in FAQS:
            conn.execute(
                "INSERT INTO faqs (question, answer, keywords) VALUES (?, ?, ?)",
                (faq["question"], faq["answer"], ",".join(faq["keywords"])),
            )
    conn.commit()
    conn.close()

def get_all_faqs():
    conn = get_connection()
    rows = conn.execute("SELECT id, question, answer, keywords FROM faqs").fetchall()
    conn.close()

    faqs = []
    for row in rows:
        faqs.append({
            "id": row["id"],
            "question": row["question"],
            "answer": row["answer"],
            "keywords": [k for k in row["keywords"].split(",") if k],
        })
    return faqs

def add_faq(question, answer, keywords):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO faqs (question, answer, keywords) VALUES (?, ?, ?)",
        (question, answer, ",".join(keywords)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id