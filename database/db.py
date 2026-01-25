import sqlite3
import os


# Always point to patients.db in the PROJECT ROOT
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "patients.db"))

print("USING DATABASE FILE:", DB_PATH)


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # ---------------- PATIENTS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- FACE EMBEDDINGS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS face_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        embedding BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    # ---------------- MEDICATIONS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        name TEXT,
        compartment INTEGER,
        start_time TEXT,
        end_time TEXT,
        last_dispensed TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    # ---------------- DISPENSE LOGS (STEP 1) ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dispense_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        patient_id INTEGER,
        patient_name TEXT,
        status TEXT,
        compartment INTEGER,
        confidence REAL
    )
    """)

    conn.commit()
    conn.close()
