
---

# 📘 Face Recognition Medication Dispenser

## (Code Walkthrough + Design Reasoning)

---

## 1️⃣ WHY THIS PROJECT EXISTS (PROBLEM STATEMENT)

Medication errors are a major risk, especially for:

* Elderly patients
* Patients with memory loss
* Patients taking multiple medications daily

Traditional pill boxes:

* Cannot verify the patient
* Cannot prevent overdose
* Cannot log medication intake

👉 **This project solves that using face recognition**, ensuring:

* Right patient
* Right medication
* Right time
* Full traceability

---

## 2️⃣ WHY FACE RECOGNITION?

### ❓ Why not PIN / RFID / Fingerprint?

| Method           | Problem                      |
| ---------------- | ---------------------------- |
| PIN              | Can be shared / forgotten    |
| RFID             | Card can be lost or misused  |
| Fingerprint      | Hygiene issues, sensor wear  |
| Face Recognition | Contactless, natural, secure |

👉 **Face recognition is non-intrusive and ideal for healthcare**.

---

## 3️⃣ WHY THIS FACE RECOGNITION APPROACH?

### ❓ Why not Haar cascades / simple OpenCV face recognition?

Because:

* Haar cascades only detect faces, they don’t identify people
* Classic OpenCV recognizers (LBPH, Eigenfaces) fail in real-world lighting

---

## 4️⃣ WHY INSIGHTFACE + EMBEDDINGS?

### 🔹 What is an embedding?

An embedding is a **numerical representation of a face** that captures identity-related features.

Instead of comparing images, we compare **vectors**.

### 🔹 Why InsightFace?

InsightFace is:

* Lightweight
* Highly accurate
* Designed for real-time systems
* Works well on low-power devices (important for Raspberry Pi)

### 🔹 Why cosine similarity?

Cosine similarity measures **angle between embeddings**, not magnitude.

This makes it:

* Robust to lighting changes
* Stable across expressions
* Industry standard for face recognition

---

## 5️⃣ WHY MULTIPLE FACE SAMPLES PER PATIENT?

People don’t look the same every time.

Multiple samples:

* Improve robustness
* Reduce false negatives
* Handle glasses, pose, lighting

👉 That’s why:

```python
patients[pid]["embeddings"].append(embedding)
```

---

## 6️⃣ CODE STRUCTURE EXPLAINED (MODULE BY MODULE)

---

### 📁 `face/utils.py`

**Purpose:**

* Detect face
* Extract embedding
* Ensure exactly one face

**Why separated?**
Single responsibility → easier debugging & replacement later.

---

### 📁 `register.py`

**Purpose:**

* Add new patients
* Capture multiple face samples
* Store embeddings

**Key design choice:**

* User can **add samples to existing patient**
* Prevents duplicate patient IDs

---

### 📁 `face/recognize.py`

**This is the brain of the system.**

It does:

1. Capture video frames
2. Detect face
3. Compare embeddings
4. Decide identity
5. Check medication
6. Apply safety rules
7. Log the event

**Important concepts inside:**

* Frame skipping → improves FPS
* Confirmation delay → prevents accidental dispense
* Cooldown → prevents overdose
* Uncertain zone → safe fallback

---

### 📁 `medication/scheduler.py`

**Purpose:**
Checks:

* Is this medication allowed **right now**?

Uses:

```python
start_time <= now <= end_time
```

👉 Keeps medical logic separate from recognition logic.

---

### 📁 `medication/dispenser.py`

**Purpose:**

* Simulate pill dispensing on laptop
* Placeholder for Raspberry Pi servo logic

Why separate?

* Laptop simulation today
* GPIO motor control tomorrow
* No code rewrite needed

---

### 📁 `tools/logger.py`

**Purpose:**

* Store every important decision
* Enable audit & traceability

Logs:

* Timestamp
* Patient
* Status
* Confidence
* Compartment

This is **critical in healthcare systems**.

---

### 📁 `database/db.py`

**Purpose:**

* Centralized DB access
* Table creation
* Safe schema evolution

Uses SQLite because:

* Lightweight
* File-based
* Perfect for embedded systems

---

## 7️⃣ WHY THRESHOLDS EXIST

```python
RECOGNITION_THRESHOLD = 0.45
UNCERTAIN_THRESHOLD = 0.35
```

### Meaning:

| Score     | Action     |
| --------- | ---------- |
| ≥ 0.45    | Recognized |
| 0.35–0.45 | Uncertain  |
| < 0.35    | Unknown    |

This prevents:

* False positives
* Unsafe dispensing

---

## 8️⃣ WHY CONFIRMATION TIME IS REQUIRED

```python
CONFIRM_SECONDS = 1.5
```

Prevents:

* Accidental face detection
* Someone walking past the camera
* Brief false recognition

---

## 9️⃣ WHY COOLDOWN IS REQUIRED

```python
DISPENSE_COOLDOWN_SECONDS = 60
```

This prevents:

* Overdose
* Repeated dispensing
* Exploitation of system

This is **a medical safety feature**.

---

## 🔟 WHY LOGGING IS CRITICAL

Every medical system must:

* Explain its decisions
* Maintain audit trails
* Support debugging

That’s why:

```python
dispense_logs
```

exists.

---

## 1️⃣1️⃣ WHY THIS DESIGN IS RASPBERRY PI READY

Because:

* Modular code
* Lightweight models
* No heavy cloud dependency
* Servo logic isolated

Only changes needed:

* Camera source
* GPIO control
* Model optimization

---

## 1️⃣2️⃣ LIMITATIONS (HONEST DISCUSSION)

* Lighting affects recognition
* Camera quality matters
* Prototype uses simulated dispensing
* Single-camera setup

👉 Mentioning limitations **increases marks**.

---

## 1️⃣3️⃣ FUTURE SCOPE

* Raspberry Pi deployment
* Mobile app dashboard
* Cloud logs
* Voice alerts
* Multi-factor authentication

---

## 🎓 HOW TO ANSWER “WHY THIS APPROACH?” IN VIVA

Say this confidently:

> “Face recognition was selected due to its non-intrusive nature and suitability for healthcare environments. InsightFace embeddings with cosine similarity provide robust recognition under varying conditions, while safety mechanisms such as confirmation delay, cooldown, and audit logging ensure reliable and secure medication dispensing.”

This is a **model answer**.

---

## ✅ FINAL NOTE (IMPORTANT)

This project is **not about face recognition alone**.

It is about:

* **Safety**
* **Decision-making**
* **System design**
* **Ethics**

You’ve built a **real engineering system**, not just a demo.

---

