from database.db import get_connection


def medication_menu():
    while True:
        print("\n--- Medication Menu ---")
        print("1. Add medication")
        print("2. View medications")
        print("3. Edit medication")
        print("4. Delete medication")
        print("5. Back")

        choice = input("Choose option: ").strip()

        if choice == "1":
            add_medication()
        elif choice == "2":
            view_medications()
        elif choice == "3":
            edit_medication()
        elif choice == "4":
            delete_medication()
        elif choice == "5":
            break
        else:
            print("[ERROR] Invalid choice")


# ---------------- ADD ----------------
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


# ---------------- VIEW ----------------
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


# ---------------- EDIT ----------------
def edit_medication():
    view_medications()
    mid = input("\nEnter medication ID to edit: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, compartment, start_time, end_time
        FROM medications
        WHERE id = ?
    """, (mid,))
    row = cur.fetchone()

    if not row:
        print("[ERROR] Medication not found")
        conn.close()
        return

    old_name, old_comp, old_start, old_end = row

    print("\nPress Enter to keep existing value")

    name = input(f"Medication name [{old_name}]: ").strip() or old_name
    comp_input = input(f"Compartment [{old_comp}]: ").strip()
    start = input(f"Start time [{old_start}]: ").strip() or old_start
    end = input(f"End time [{old_end}]: ").strip() or old_end

    compartment = int(comp_input) if comp_input else old_comp

    if not valid_time(start) or not valid_time(end):
        print("[ERROR] Invalid time format")
        conn.close()
        return

    cur.execute("""
        UPDATE medications
        SET name = ?, compartment = ?, start_time = ?, end_time = ?
        WHERE id = ?
    """, (name, compartment, start, end, mid))

    conn.commit()
    conn.close()
    print("[SUCCESS] Medication updated")


# ---------------- DELETE ----------------
def delete_medication():
    view_medications()
    mid = input("\nEnter medication ID to delete: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM medications WHERE id = ?", (mid,))
    conn.commit()
    conn.close()

    print("[SUCCESS] Medication deleted")


# ---------------- VALIDATION ----------------s
def valid_time(t):
    try:
        h, m = t.split(":")
        return 0 <= int(h) < 24 and 0 <= int(m) < 60
    except:
        return False
