import cv2
import numpy as np
import time

from face.utils import get_face_embedding
from database.db import get_connection
from medication.scheduler import check_medication
from medication.dispenser import dispense_medication
from tools.logger import log_event


# ---------------- CONFIG ----------------
RECOGNITION_THRESHOLD = 0.45
UNCERTAIN_THRESHOLD   = 0.35
CONFIRM_SECONDS       = 2.5
PROCESS_EVERY_N       = 5
DISPLAY_HOLD_TIME     = 0.8
RESIZE_SCALE          = 0.5
DISPENSE_COOLDOWN_SECONDS = 60   # safety lock
# ----------------------------------------


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

def safe_log(patient
    prev = last_logged_status.get(patient_id)
    if prev == status:
        return  # avoid duplicate logs

    log_event(
        patient_id=patient_id,
        patient_name=patient_name,
        status=status,
        compartment=compartment,
        confidence=confidence
    )

    last_logged_status[patient_id] = status


def recognize_face():
    known_faces = load_embeddings()
    last_dispense_time = {}

    if not known_faces:
        print("[ERROR] No registered patients found")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[CRITICAL] Camera not detected. System paused.")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[INFO] Face recognition started (press 'q' to quit)")

    frame_count = 0
    confirmed_patient_id = None
    confirm_start_time = None
    last_logged_status = {}

    fps_start_time = time.time()
    fps_frame_count = 0
    current_fps = 0
    display_state = {
        "label": None,
        "color": None,
        "bbox": None,
        "time": 0
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Camera frame lost. Retrying...")
            time.sleep(0.5)
            continue
        frame_count +=1
        # ---------- FPS UPDATE ----------
        fps_frame_count += 1
        elapsed = time.time() - fps_start_time

        if elapsed >= 1.0:
            current_fps = fps_frame_count / elapsed
            fps_frame_count = 0
            fps_start_time = time.time()


        # ---------- FRAME SKIP ----------
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

            cv2.imshow("Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        # --------------------------------

        # ---------- FACE DETECTION ----------
        small = cv2.resize(frame, None, fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        embedding, bbox, face_count = get_face_embedding(small)

        if face_count == 0:
            last_logged_status.clear()
            confirmed_patient_id = None
            confirm_start_time = None

            display_state.update({
                "label": "NO FACE DETECTED",
                "color": (0, 0, 255),
                "bbox": None,
                "time": time.time()
            })
            cv2.imshow("Face Recognition", frame)
            continue

        if face_count > 1:
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

        
        # ---------- DECISION ----------
        if best_score >= RECOGNITION_THRESHOLD:
            status, result = check_medication(best_id)

            if status == "ERROR":
                label = "SYSTEM ERROR"
                color = (0, 0, 255)

                safe_log(
                    patient_id=best_id,
                    patient_name=best_name,
                    status="SYSTEM_ERROR",
                    compartment=None,
                    confidence=best_score,
                    last_logged_status=last_logged_status
                )

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

                        safe_log(
                            best_id, best_name, "WAIT",
                            None, best_score, last_logged_status
                        )

                    elif elapsed >= CONFIRM_SECONDS:
                        dispense_medication(result["compartment"])
                        last_dispense_time[best_id] = now

                        label = f"{best_name} | DISPENSED ({best_score:.2f})"
                        color = (0, 255, 0)

                        safe_log(
                            best_id, best_name, "DISPENSED",
                            result["compartment"], best_score, last_logged_status
                        )

                        confirmed_patient_id = None
                        confirm_start_time = None

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

                safe_log(
                    best_id, best_name, "NOT_TIME",
                    None, best_score, last_logged_status
                )

                confirmed_patient_id = None
                confirm_start_time = None

            else:  # BLOCKED
                label = f"{best_name} | ALREADY TAKEN ({best_score:.2f})"
                color = (0, 165, 255)

                safe_log(
                    best_id, best_name, "ALREADY_TAKEN",
                    None, best_score, last_logged_status
                )

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
        display_state.update({
            "label": label,
            "color": color,
            "bbox": bbox,
            "time": time.time()
        })

        # ---------- DRAW ----------
        x1, y1, x2, y2 = bbox
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


        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
