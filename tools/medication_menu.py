from database.db import get_connection


def medication_menu():
    while True:
        print("\n--- Medication Menu ---")
        print("1. Add medication")
        print("2. View medications")
        print("3. Delete medication")
        print("4. Back")

        choice = input("Choose option: ").strip()

        if choice == "1":
            add_medication()
        elif choice == "2":
            view_medications()
        elif choice == "3":
            delete_medication()
        elif choice == "4":
            break
        else:
            print("[ERROR] Invalid choice")


def add_medication():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM patients")
    patients = cur.fetchall()

    if not patients:
        print("[ERROR] No patients found")
        return

    print("\nPatients:")
    for pid, name in patients:
        print(f"{pid}: {name}")

    patient_id = int(input("Enter patient ID: "))
    name = input("Medication name: ").strip()
    compartment = int(input("Compartment number (1–3): "))

    start = input("Start time (HH:MM): ").strip()
    end = input("End time (HH:MM): ").strip()

    # --- validation ---
    if not valid_time(start) or not valid_time(end):
        print("[ERROR] Invalid time format")
        return

    cur.execute("""
        INSERT INTO medications (patient_id, name, compartment, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, name, compartment, start, end))

    conn.commit()
    conn.close()

    print("[SUCCESS] Medication added")


def view_medications():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id, p.name, m.name, m.compartment, m.start_time, m.end_time
        FROM medications m
        JOIN patients p ON p.id = m.patient_id
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No medications found")
        return

    print("\nMedications:")
    for mid, patient, med, comp, start, end in rows:
        print(f"{mid}. {patient} | {med} | Comp {comp} | {start}–{end}")


def delete_medication():
    view_medications()
    mid = input("\nEnter medication ID to delete: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM medications WHERE id = ?", (mid,))
    conn.commit()
    conn.close()

    print("[SUCCESS] Medication deleted")


def valid_time(t):
    try:
        h, m = t.split(":")
        return 0 <= int(h) < 24 and 0 <= int(m) < 60
    except:
        return False
