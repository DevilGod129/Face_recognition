
---

```markdown
# 🧠 Face Recognition Based Medication Dispensing System

## 📌 Project Overview
This project is an intelligent medication dispensing system that uses **face recognition** to identify patients and dispense medication at scheduled times.  
The system is designed to reduce medication errors, prevent overdosing, and improve patient safety—especially for elderly or dependent patients.

The current implementation runs on a **laptop (simulation mode)** and is designed to be **easily deployable on Raspberry Pi** in future stages.

---

## 🎯 Key Features
- Face-based patient identification
- Multiple face samples per patient for robustness
- Medication scheduling with time windows
- Safety mechanisms (confirmation delay & cooldown)
- Prevention of wrong-person dispensing
- Full audit logging (timestamp, patient, confidence, action)
- Modular and Raspberry Pi–ready architecture

---

## 🏗️ System Architecture (High-Level)

```

Camera
↓
Face Detection & Embedding Extraction
↓
Face Recognition (Cosine Similarity)
↓
Medication Scheduler
↓
Safety Checks (Confirmation + Cooldown)
↓
Dispense Simulator / Servo (Future)
↓
Logging System (SQLite)

```

---

## 📂 Project Structure

```

project/
│
├── face/
│   ├── utils.py              # Face detection & embedding extraction
│   └── recognize.py          # Face recognition & decision logic
│
├── medication/
│   ├── scheduler.py          # Medication time checking
│   └── dispenser.py          # Dispense simulation (servo later)
│
├── database/
│   └── db.py                 # SQLite connection & table creation
│
├── tools/
│   └── logger.py             # Audit logging & log viewer
│
├── register.py               # Patient registration & sample capture
├── main.py                   # Application entry point
├── patients.db               # SQLite database (ignored in git)
├── README.md                 # Project documentation
└── .gitignore

````

---

## 🧠 How the System Works (Flow)

1. Camera captures live video frames.
2. Face is detected and converted into an embedding vector.
3. Embedding is compared with stored patient embeddings.
4. Cosine similarity score determines recognition confidence.
5. If recognized:
   - Medication schedule is checked.
   - Safety confirmation and cooldown are applied.
6. Medication is dispensed (simulated on laptop).
7. All decisions are logged in the database.

---

## 🧪 Safety Mechanisms
- **Recognition Threshold**: Prevents false positives
- **Uncertain Zone**: Graceful degradation instead of forced decisions
- **Confirmation Delay**: Ensures patient intent
- **Cooldown Period**: Prevents overdose
- **Multiple Faces Detection**: Blocks unsafe conditions
- **Audit Logs**: Full traceability

---

## 🗄️ Database Design

### Tables
- `patients` – Patient identity
- `face_embeddings` – Multiple embeddings per patient
- `medications` – Medication schedules
- `dispense_logs` – Audit trail (timestamp, status, confidence)

---

## 📊 Viewing Logs

To view recent system logs:

```bash
python
````

```python
from tools.logger import view_logs
view_logs()
```

Example output:

```
('2026-01-25 10:21:08', 'Patient A', 'DISPENSED', 1, 0.62)
('2026-01-25 10:21:20', 'Patient A', 'WAIT', None, 0.60)
```

---

## 💻 Running the Project (Laptop Simulation)

### 1️⃣ Install dependencies

```bash
pip install opencv-python numpy insightface
```

### 2️⃣ Create database tables (run once)

```bash
python -c "from database.db import create_tables; create_tables()"
```

### 3️⃣ Register a patient

```bash
python register.py
```

### 4️⃣ Add medication schedules

```bash
python main.py
# choose medication menu option
```

### 5️⃣ Start recognition

```bash
python main.py
# choose recognition option
```

---

## 🍓 Raspberry Pi Deployment (Planned)

### Future Changes Required:

* Replace webcam with Pi Camera
* Replace dispense simulator with servo motor control (GPIO)
* Reduce model size for Pi performance
* Optional cloud-based dashboard
* Optional mobile app for caregivers

> The current codebase is modular and designed to support Raspberry Pi deployment with minimal changes.

---

## ⚠️ Limitations

* Performance depends on lighting conditions
* Camera quality affects recognition accuracy
* Dispensing is currently simulated
* Single-camera setup

---

## 🚀 Future Enhancements

* Raspberry Pi + servo integration
* Mobile app dashboard
* Cloud-based logging
* Voice alerts & emergency notifications
* Multi-factor authentication (face + voice)

---

## 🎓 Academic Relevance

This project demonstrates:

* Computer vision in healthcare
* AI-based biometric authentication
* Embedded system design
* Safety-critical system development
* Ethical handling of biometric data

---

## 👤 Author

Minor Project
Face Recognition Based Medication Dispensing System

---

## 📝 License

This project is developed for academic purposes.

