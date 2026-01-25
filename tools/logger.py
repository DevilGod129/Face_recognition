from datetime import datetime
from database.db import get_connection


def log_event(patient_id, patient_name, status, compartment=None, confidence=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO dispense_logs
        (timestamp, patient_id, patient_name, status, compartment, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        patient_id,
        patient_name,
        status,
        compartment,
        confidence
    ))

    conn.commit()
    conn.close()


def view_logs(limit=20):
    """
    Development helper: prints last N dispense events
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, patient_name, status, compartment, confidence
        FROM dispense_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    print("\n--- RECENT DISPENSE LOGS ---")
    for row in rows:
        print(row)
