from datetime import datetime
from database.db import get_connection

def check_medication(patient_id):
    now_time = datetime.now().time()
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, compartment, start_time, end_time, last_dispensed
    FROM medications
    WHERE patient_id = ?
    """, (patient_id,))

    meds = cur.fetchall()
    conn.close()

    print("DEBUG meds:", meds)
    print("DEBUG now:", now_time)

    for med in meds:
        med_id, name, compartment, start, end, last = med

        # convert DB strings to time objects
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()

        print("DEBUG checking:", start_time, "<=", now_time, "<=", end_time)

        if last == today:
            return "BLOCKED", {
                "reason": "ALREADY_DISPENSED",
                "name": name
            }


        # NORMAL window (same day)
        if start_time <= now_time <= end_time:
            return "DISPENSE", {
                "med_id": med_id,
                "name": name,
                "compartment": compartment
            }

    return "WARNING", "No medication scheduled right now"
