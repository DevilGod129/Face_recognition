import cv2
from database.db import get_connection
from face.utils import get_face_embedding

SAMPLES_REQUIRED = 20   # Increased for better accuracy
RESIZE_SCALE = 0.7


def choose_patient():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM patients")
    patients = cur.fetchall()

    if patients:
        print("\nExisting patients:")
        for pid, name in patients:
            print(f"{pid}: {name}")

        choice = input(
            "\nEnter patient ID to ADD samples\n"
            "or press Enter to CREATE new patient: "
        )

        if choice.strip():
            conn.close()
            return int(choice)

    # Create new patient
    name = input("Enter new patient name: ").strip()
    cur.execute("INSERT INTO patients (name) VALUES (?)", (name,))
    conn.commit()
    pid = cur.lastrowid
    conn.close()

    print(f"[INFO] Created new patient: {name} (ID: {pid})")
    return pid


def register_patient():
    patient_id = choose_patient()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    conn = get_connection()
    cur = conn.cursor()

    collected = 0
    print(f"[INFO] Capturing samples for patient ID: {patient_id}")
    print("[INFO] Press 'c' to capture | 'q' to quit")

    while collected < SAMPLES_REQUIRED:
        ret, frame = cap.read()
        if not ret:
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
