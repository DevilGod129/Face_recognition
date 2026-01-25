from database.db import get_connection

def delete_patient():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM patients")
    patients = cur.fetchall()

    if not patients:
        print("[ERROR] No patients found")
        conn.close()
        return

    print("\nPatients:")
    for pid, name in patients:
        print(f"{pid}: {name}")

    pid = input("\nEnter patient ID to delete: ").strip()
    confirm = input("Type DELETE to confirm: ").strip()

    if confirm != "DELETE":
        print("[CANCELLED] Patient not deleted")
        conn.close()
        return

    # ---- SAFE CASCADE DELETE ----
    cur.execute("DELETE FROM face_embeddings WHERE patient_id = ?", (pid,))
    cur.execute("DELETE FROM medications WHERE patient_id = ?", (pid,))
    cur.execute("DELETE FROM dispense_logs WHERE patient_id = ?", (pid,))
    cur.execute("DELETE FROM patients WHERE id = ?", (pid,))

    conn.commit()
    conn.close()

    print("[SUCCESS] Patient and all related data deleted")
