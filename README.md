---

```markdown
# 🧠 Face Recognition Based Medication Dispensing System

## 📌 Project Overview
This project is an **intelligent, safety-critical medication dispensing system** that uses **face recognition** to identify patients and dispense medication at scheduled times.

The system is designed to:
- Reduce medication errors
- Prevent overdosing
- Ensure the *right patient receives the right medication at the right time*

The current implementation runs in **laptop simulation mode** and is **architected for seamless Raspberry Pi deployment** in later stages.

---

## 🎯 Key Features

- Face-based patient identification (no cards, no passwords)
- Multiple face samples per patient for robust recognition
- Confidence-based recognition using cosine similarity
- Medication scheduling with configurable time windows
- Confirmation delay to ensure patient intent
- Cooldown mechanism to prevent repeated dispensing
- Blocking of unsafe conditions (unknown face / multiple faces)
- Event-based audit logging (no duplicate logs)
- Real-time FPS monitoring and performance optimization
- Modular, Raspberry Pi–ready architecture

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
Safety Layer
(Confirmation + Cooldown + Multi-Face Blocking)
↓
Dispense Module (Simulated / Servo on Pi)
↓
Audit Logging (SQLite)

```

---

## 📂 Project Structure

```

project/
│
├── face/
│   ├── utils.py              # Face detection & embedding extraction
│   └── recognize.py          # Recognition, safety logic & FPS control
│
├── medication/
│   ├── scheduler.py          # Medication time window logic
│   └── dispenser.py          # Dispense simulation (GPIO later)
│
├── database/
│   └── db.py                 # SQLite connection & schema
│
├── tools/
│   └── logger.py             # Event-based audit logging
│
├── register.py               # Patient registration & sample capture
├── main.py                   # Menu-driven application entry point
├── patients.db               # SQLite database (ignored in git)
├── README.md
└── .gitignore

```

---

## 🧠 How the System Works (Detailed Flow)

1. Camera captures live video frames.
2. Face is detected and converted into an embedding vector.
3. Embedding is compared with stored patient embeddings.
4. Cosine similarity score determines recognition confidence.
5. If confidence ≥ threshold:
   - Medication schedule is checked.
   - Safety confirmation timer is started.
6. If confirmed and safe:
   - Cooldown is verified.
   - Medication is dispensed (simulated).
7. Every **state change** is logged in the database.
8. FPS is monitored continuously to ensure real-time performance.

---

## 🧪 Safety Mechanisms (Core Design Principle)

This system is designed as a **safety-critical prototype**.

### Implemented Safety Layers

- **Recognition Threshold**  
  Prevents false positives.
- **Uncertain Zone Handling**  
  Avoids forced decisions.
- **Confirmation Delay**  
  Ensures patient intent before dispensing.
- **Cooldown Lock**  
  Prevents overdose or rapid re-dispensing.
- **Multiple Face Detection**  
  Blocks unsafe scenarios.
- **Camera & Database Fail-Safes**  
  System halts safely on critical failure.
- **Event-Based Logging**  
  Ensures traceability without database spam.

---

## 🗄️ Database Design

### Tables

- `patients` – Patient identity
- `face_embeddings` – Multiple embeddings per patient
- `medications` – Medication schedules
- `dispense_logs` – Audit trail with:
  - Timestamp
  - Patient
  - Action (DISPENSED, WAIT, NOT_TIME, etc.)
  - Confidence score

---

## 📊 Viewing Logs

To inspect system logs:

```bash
python
```

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

### 1️⃣ Install Dependencies

```bash
pip install opencv-python numpy insightface
```

### 2️⃣ Create Database Tables (Run Once)

```bash
python -c "from database.db import create_tables; create_tables()"
```

### 3️⃣ Register a Patient

```bash
python register.py
```

Capture multiple face samples for robustness.

### 4️⃣ Add Medication Schedules

```bash
python main.py
# Select medication menu
```

### 5️⃣ Start Face Recognition

```bash
python main.py
# Select recognition option
```

FPS and recognition confidence will be displayed on screen.

---

## 🍓 Raspberry Pi Deployment (Planned)

### Planned Modifications

- Replace webcam with Raspberry Pi Camera
- Replace dispense simulator with servo motor (GPIO)
- Adjust frame skipping and resolution for Pi performance
- Optional cloud-based dashboard
- Optional caregiver mobile application

> The current codebase is modular and intentionally designed to support Raspberry Pi deployment with minimal changes.

---

## ⚠️ Limitations

- Recognition accuracy depends on lighting conditions
- Camera quality impacts performance
- Dispensing is currently simulated
- Single-camera setup

---

## 🚀 Future Enhancements

- Raspberry Pi + servo motor integration
- Web & mobile dashboard for caregivers
- Cloud-based monitoring
- Voice alerts and emergency notifications
- Multi-factor authentication (face + voice)

---

## 🎓 Academic Relevance

This project demonstrates:

- Computer vision in healthcare
- Biometric authentication
- Safety-critical system design
- Embedded system architecture
- Ethical handling of biometric data
- Real-time performance optimization

---

## 👤 Author

Minor Project
**Face Recognition Based Medication Dispensing System**

---

## 📝 License

Developed strictly for academic and research purposes.

```

```
