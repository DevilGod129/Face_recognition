
import cv2
import requests
from database.db import get_connection
from face.utils import get_face_embedding
PATIENT_API = "http://192.168.137.1:8000/api/patients"
SAMPLES_REQUIRED = 15   # Increased for better accuracy
RESIZE_SCALE = 0.5

def choose_patient():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM patients")
    patients = cur.fetchall()

    if not patients:
        print("[INFO] No existing patients. Creating new.")
        patient_id = create_new_patient(cur)
        conn.commit()
        conn.close()
        return patient_id

    print("\nExisting patients:")
    for pid, name in patients:
        print(f"{pid}: {name}")

    while True:
        choice = input(
            "\nEnter PATIENT ID to add samples "
            "(or press Enter to create NEW patient): "
        ).strip()

        # Create new patient
        if choice == "":
            patient_id = create_new_patient(cur)
            conn.commit()
            conn.close()
            return patient_id

        # Must be numeric
        if not choice.isdigit():
            print("[ERROR] Please enter a numeric patient ID.")
            continue

        patient_id = int(choice)

        # Validate ID exists
        if any(pid == patient_id for pid, _ in patients):
            conn.close()
            return patient_id
        else:
            print("[ERROR] Invalid patient ID. Try again.")
def sync_patients():

    print("[SYNC] Fetching patients from backend...")

    try:
        response = requests.get(PATIENT_API)
        patients = response.json()

        conn = get_connection()
        cur = conn.cursor()

        for p in patients:
            cur.execute("""
            INSERT OR REPLACE INTO patients (id, name)
            VALUES (?, ?)
            """, (p["id"], p["name"]))

        conn.commit()
        conn.close()

        print("[SYNC] Patients synced:", len(patients))

    except Exception as e:
        print("[SYNC ERROR]", e)
            

def create_new_patient(cur):
    name = input("Enter new patient name: ").strip()

    if not name:
        print("[ERROR] Name cannot be empty.")
        return create_new_patient(cur)

    # Send patient to backend
    try:
        response = requests.post(
            "http://192.168.137.1:8000/api/patients",
            json={"name": name}
        )

        response.raise_for_status()
        patient = response.json()

        patient_id = patient["id"]

        print(f"[SUCCESS] Patient '{name}' created in backend with ID {patient_id}")

    except Exception as e:
        print("[ERROR] Failed to create patient in backend:", e)
        exit()

    # Store locally using SAME ID
    cur.execute(
        "INSERT OR IGNORE INTO patients (id, name) VALUES (?, ?)",
        (patient_id, name)
    )

    return patient_id

def register_patient():
    sync_patients()
    patient_id = choose_patient()

    # -------- CAMERA SETUP --------
    cap = None

    for i in [0, 1]:
        test_cap = cv2.VideoCapture(i)
        ret, frame = test_cap.read()

        if ret:
            print(f"[SUCCESS] Using camera index: {i}")
            cap = test_cap
            break
        else:
            print(f"[FAIL] Camera index {i} not working")
            test_cap.release()

    if cap is None:
        print("[CRITICAL] No working camera found")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    # -------- DB SETUP --------
    conn = get_connection()
    cur = conn.cursor()
    collected = 0
    print(f"[INFO] Capturing samples for patient ID: {patient_id}")
    print("[INFO] Press 'c' to capture | 'q' to quit")

    while collected < SAMPLES_REQUIRED:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read from camera")	 
            continue

        small = cv2.resize(frame, None, fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        embedding, bbox, face_count = get_face_embedding(small)

        display = frame.copy()

        if bbox is not None:
            bbox = (bbox / RESIZE_SCALE).astype(int)

        if face_count > 1:
            cv2.putText(
                display, "ONLY ONE FACE ALLOWED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 255), 2
            )

        elif bbox is not None:
            x1, y1, x2, y2 = bbox
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(
            display,
            f"Samples: {collected}/{SAMPLES_REQUIRED}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX, 1,
            (0, 255, 0), 2
        )

        cv2.imshow("Face Registration", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        if key == ord('c'):
            if embedding is None or face_count != 1:
                print("[WARN] Ensure exactly ONE face is visible")
                continue

            cur.execute(
                "INSERT INTO face_embeddings (patient_id, embedding) VALUES (?, ?)",
                (patient_id, embedding.tobytes())
            )
            conn.commit()
            collected += 1
            print(f"[INFO] Captured sample {collected}")
                        
           
    cap.release()
    cv2.destroyAllWindows()
    conn.close()

    print("[SUCCESS] Face samples saved successfully")
