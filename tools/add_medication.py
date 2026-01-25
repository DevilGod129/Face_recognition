import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.db import get_connection
from datetime import datetime, timedelta


conn = get_connection()
cur = conn.cursor()

# Show patients
cur.execute("SELECT id, name FROM patients")
patients = cur.fetchall()

if not patients:
    print("❌ No patients found.")
    exit()

print("\nPatients:")
for pid, name in patients:
    print(f"{pid}: {name}")

patient_id = int(input("\nEnter patient ID: "))
med_name = input("Medicine name: ")
compartment = int(input("Compartment number (1/2/3): "))

hours = int(input("Valid for how many HOURS from now? "))

now = datetime.now()
start = now.strftime("%H:%M")
end = (now + timedelta(hours=hours)).strftime("%H:%M")

cur.execute("""
INSERT INTO medications
(patient_id, name, compartment, start_time, end_time, last_dispensed)
VALUES (?, ?, ?, ?, ?, NULL)
""", (patient_id, med_name, compartment, start, end))

conn.commit()
conn.close()

print("\n✅ Medication added successfully")
print("Time window:", start, "to", end)
