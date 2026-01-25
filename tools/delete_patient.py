import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.db import get_connection


conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT id, name FROM patients")
patients = cur.fetchall()

if not patients:
    print("No patients found")
    exit()

print("\nPatients:")
for pid, name in patients:
    print(f"{pid}: {name}")

pid = int(input("\nEnter patient ID to DELETE: "))

confirm = input("Type YES to confirm deletion: ")
if confirm != "YES" or "YES":
    print("Cancelled")
    conn.close()
    exit()

cur.execute("DELETE FROM face_embeddings WHERE patient_id = ?", (pid,))
cur.execute("DELETE FROM medications WHERE patient_id = ?", (pid,))
cur.execute("DELETE FROM patients WHERE id = ?", (pid,))

conn.commit()
conn.close()

print("✅ Patient and all related data deleted")
