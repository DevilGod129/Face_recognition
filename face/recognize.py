import cv2
import numpy as np
import time
import requests

PATIENT_API = "http://192.168.137.1:8000/api/patients"
MEDICATION_API= "http://192.168.137.1:8000/api/medications" #replace IP
LOG_API="http://192.168.137.1:8000/api/logs"
API_KEY = "supersecretkey123"
SYNC_INTERVAL = 30 # 5 minutes

from face.utils import get_face_embedding
from database.db import get_connection
from medication.scheduler import check_medication
from medication.dispenser import dispense_medication
from datetime import datetime
from database.db import get_connection


# ---------------- CONFIG ----------------
RECOGNITION_THRESHOLD = 0.45
UNCERTAIN_THRESHOLD   = 0.35
CONFIRM_SECONDS       = 3.5
PROCESS_EVERY_N       = 12
DISPLAY_HOLD_TIME     = 1.0
RESIZE_SCALE          = 0.4
DISPENSE_COOLDOWN_SECONDS = 60   # safety lock
STABLE_FRAMES_REQUIRED = 4
# ----------------------------------------
DEBUG = False


def update_backend_medication(med_id):
    try:
        response = requests.put(
            f"http://192.168.137.1:8000/api/medications/{med_id}/dispense"
        )
        print("[SYNC] Backend medication updated:", response.status_code)
    except Exception as e:
        print("[SYNC ERROR]", e)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_embeddings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.id, p.name, f.embedding
        FROM patients p
        JOIN face_embeddings f ON p.id = f.patient_id
    """)

    rows = cur.fetchall()
    conn.close()

    patients = {}
    for pid, name, emb in rows:
        emb_np = np.frombuffer(emb, dtype=np.float32)
        patients.setdefault(pid, {"name": name, "embeddings": []})
        patients[pid]["embeddings"].append(emb_np)

    return patients

def capture_photo(cap):

    ret, frame = cap.read()

    if not ret:
        print("[PHOTO] Failed to capture image")
        return None

    filename = "dispense.jpg"
    cv2.imwrite(filename, frame)

    return filename


def send_log_to_backend(patient_id, status, compartment, confidence, image_path=None):

    headers = {
        "x-api-key": API_KEY
    }

    data = {
        "status": str(status),
        "compartment": str(compartment),
        "confidence": str(confidence),
        "patient_id": str(patient_id)
    }

    files = None

    if image_path:
        try:
            files = {
                "image": ("dispense.jpg", open(image_path, "rb"), "image/jpeg")
            }
        except:
            files = None

    try:
        response = requests.post(
            LOG_API,
            data=data,     # must be form data
            files=files,   # optional image
            headers=headers,
            timeout=5
        )

        print("[LOG] Sent to backend:", response.status_code)
        print("[LOG RESPONSE]", response.text)

    except Exception as e:
        print("[LOG ERROR]", e)



def sync_patients():

    try:
        print("[SYNC] Fetching patients from backend...")

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



def sync_medications():
    try:
        print("[SYNC] Fetching medications from backend...")
        response = requests.get(MEDICATION_API, timeout=5)
        response.raise_for_status()
        meds = response.json()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS medications (
         id INTEGER PRIMARY KEY,
         patient_id INTEGER,
         name TEXT,
         compartment INTEGER,
         start_time TEXT,
             end_time TEXT,
         last_dispensed TEXT
            )
    """)

        cur.execute("DELETE FROM medications")
        for med in meds:
            cur.execute("""
                        INSERT OR REPLACE INTO medications
                        (id, patient_id, name, compartment, start_time, end_time, last_dispensed)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                        med["id"],
                        med["patient_id"],
                        med["name"],
                        med["compartment"],
                        med["start_time"],
                        med["end_time"],
                        med.get("last_dispensed")
))


        conn.commit()
        conn.close()

        print("[SYNC] Success. Inserted:", len(meds))

    except Exception as e:
        print("[SYNC] Failed:", e)


def recognize_face_with_exit():
    known_faces = load_embeddings()
    last_sync_time = 0
    last_check_time =0
    CHECK_INTERVAL = 2
    sync_patients()
    sync_medications()
    last_dispense_time = {}

    if not known_faces:
        print("[ERROR] No registered patients found")
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        print("[CRITICAL] Camera not detected. System paused.")
        return
    else:
        print("Camera opened successfully")


    print("[INFO] Face recognition started (press 'q' to quit)")

    frame_count = 0
    confirmed_patient_id = None
    confirm_start_time = None
    last_logged_status = {}

    fps_start_time = time.time()
    fps_frame_count = 0
    current_fps = 0
    '''
    while DEBUG:
        display_state = {
            "label": None,
            "color": None,
            "bbox": None,
            "time": 0
        }
'''
    while True:
        
        #----- PERIODIC SYNC---#
        current_time = time.time()
        if current_time - last_sync_time>= SYNC_INTERVAL:
            sync_medications()
            last_sync_time = current_time
       #---------------------
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Camera frame lost. Retrying...")
            cap.release()
            time.sleep(1)
            cap =cv2.VideoCapture(0)
            continue
        frame_count +=1
        # ---------- FPS UPDATE ----------
        fps_frame_count += 1
        elapsed = time.time() - fps_start_time

        if elapsed >= 1.0:
            current_fps = fps_frame_count / elapsed
            fps_frame_count = 0
            fps_start_time = time.time()


        '''
        while DEBUG:# ---------- FRAME SKIP ----------
            if frame_count % PROCESS_EVERY_N != 0:
                now = time.time()
                if (
                    display_state["bbox"] is not None and
                    (now - display_state["time"]) <= DISPLAY_HOLD_TIME
                ):
                    x1, y1, x2, y2 = display_state["bbox"]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), display_state["color"], 2)
                    cv2.putText(
                        frame,
                        display_state["label"],
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        display_state["color"],
                        2
                    )
                    cv2.putText(
                        frame,
                        f"FPS: {current_fps:.1f}",
                        (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
            if DEBUG:
                cv2.imshow("Face Recognition", frame)
            if DEBUG:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            continue
        # --------------------------------
'''
        # ---------- FACE DETECTION ----------
        small = cv2.resize(frame, None, fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        embedding, bbox, face_count = get_face_embedding(small)

        if face_count == 0:
            last_logged_status.clear()
            confirmed_patient_id = None
            confirm_start_time = None
            if DEBUG:
                display_state.update({
                    "label": "NO FACE DETECTED",
                    "color": (0, 0, 255),
                    "bbox": None,
                    "time": time.time()
                })
            if DEBUG:
                cv2.imshow("Face Recognition", frame)
            continue

        if face_count > 1:
            if DEBUG:
                display_state.update({
                    "label": "MULTIPLE FACES DETECTED",
                    "color": (0, 0, 255),
                    "bbox": None,
                    "time": time.time()
                })
                cv2.putText(
                    frame,
                    "MULTIPLE FACES DETECTED",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    3
                )
            if DEBUG:
                cv2.imshow("Face Recognition", frame)
            continue

        # ---------- SCALE BBOX ----------
        x1, y1, x2, y2 = bbox
        bbox = (
            int(x1 / RESIZE_SCALE),
            int(y1 / RESIZE_SCALE),
            int(x2 / RESIZE_SCALE),
            int(y2 / RESIZE_SCALE)
        )

        # ---------- MATCHING ----------
        best_score = 0
        best_id = None
        best_name = None

        for pid, data in known_faces.items():
            scores = [cosine_similarity(embedding, e) for e in data["embeddings"]]
            score = max(scores)
            if score > best_score:
                best_score = score
                best_id = pid
                best_name = data["name"]
        
        
        print(f"RECOGNIZED PATIENT ID: {best_id} | NAME: {best_name} | SCORE: {best_score:.2f}")

        
        # ---------- DECISION ----------
        if best_score >= RECOGNITION_THRESHOLD:
            
            now_time = time.time()
            if now_time - last_check_time < CHECK_INTERVAL:
                 continue
            last_check_time = now_time
            print(f"[CALLING CHECK] patient={best_id}")
            status,result = check_medication(best_id)
            print(f"[CHECK] Patient {best_id} | Status: {status}")

            if status == "ERROR":
                label = "SYSTEM ERROR"
                color = (0, 0, 255)

                
                

                confirmed_patient_id = None
                confirm_start_time = None

            elif status == "DISPENSE":
                now = time.time()

                if confirmed_patient_id == best_id:
                    elapsed = now - confirm_start_time
                    last_time = last_dispense_time.get(best_id)

                    if last_time and (now - last_time) < DISPENSE_COOLDOWN_SECONDS:
                        remaining = int(DISPENSE_COOLDOWN_SECONDS - (now - last_time))
                        label = f"{best_name} | WAIT {remaining}s"
                        color = (0, 0, 255)

                    elif elapsed >= CONFIRM_SECONDS:
                        med_id = result["medication_id"]

                        # -------- BACKEND FIRST --------
                        try:
                            response = requests.put(
                                f"http://192.168.137.1:8000/api/medications/{med_id}/dispense",
                                timeout=5
                            )

                            print("[BACKEND RESPONSE]", response.status_code, response.text)

                            if response.status_code != 200:
                                label = f"{best_name} | BLOCKED BY BACKEND"
                                color = (0, 0, 255)
                                last_dispense_time[best_id]=now

                                confirmed_patient_id = None
                                confirm_start_time = None
                                continue

                        except Exception as e:
                            print("[BACKEND ERROR]", e)
                            continue

                        # -------- ONLY IF APPROVED --------
                        #dispense_medication(result["compartment"])
                        compartment = result["compartment"]
                        last_dispense_time[best_id] = now
                        # -------- LOCAL UPDATE --------
                        conn = get_connection()
                        cur = conn.cursor()

                        cur.execute("""
                        UPDATE medications
                        SET last_dispensed = ?
                        WHERE id = ?
                        """, (
                            datetime.now().isoformat(),
                            med_id
                        ))

                        conn.commit()
                        conn.close()

                        # -------- PHOTO --------
                        photo = capture_photo(cap)

                        # -------- LOG --------
                        send_log_to_backend(
                            best_id,
                            "DISPENSED",
                            result["compartment"],
                            best_score,
                            photo
                        )

                        return result["compartment"]
                    else:
                        label = f"{best_name} | CONFIRMING {elapsed:.1f}s"
                        color = (0, 200, 0)

                else:
                    confirmed_patient_id = best_id
                    confirm_start_time = now
                    label = f"{best_name} | HOLD STILL ({best_score:.2f})"
                    color = (0, 200, 0)

            elif status == "WARNING":
                label = f"{best_name} | NOT TIME ({best_score:.2f})"
                color = (255, 255, 0)

               

                confirmed_patient_id = None
                confirm_start_time = None

            else:  # BLOCKED
                label = f"{best_name} | ALREADY TAKEN ({best_score:.2f})"
                color = (0, 165, 255)


                confirmed_patient_id = None
                confirm_start_time = None

        elif best_score >= UNCERTAIN_THRESHOLD:
            label = f"Uncertain ({best_score:.2f})"
            color = (0, 255, 255)
            confirmed_patient_id = None
            confirm_start_time = None

        else:
            label = "Unknown"
            color = (0, 0, 255)
            confirmed_patient_id = None
            confirm_start_time = None

        
        # ---------- UPDATE DISPLAY ----------
        if DEBUG:
            display_state.update({
                "label": label,
                "color": color,
                "bbox": bbox,
                "time": time.time()
            })

        # ---------- DRAW ----------
        x1, y1, x2, y2 = bbox
        if DEBUG:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )
            cv2.putText(
                frame,
                f"FPS: {current_fps:.1f}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        if DEBUG:
            cv2.imshow("Face Recognition", frame)
        if DEBUG:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
def recognize_once():
    """
    Runs recognition until ONE successful dispense happens,
    then returns True.
    """

    from medication.scheduler import check_medication
    from medication.dispenser import dispense_medication

    print("[ROBOT] Starting single recognition cycle...")

    # Call original function but stop after first dispense
    # 👉 SIMPLE APPROACH: reuse recognize_face but exit early

    result = recognize_face_with_exit()

    return result
