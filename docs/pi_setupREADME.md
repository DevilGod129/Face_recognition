---

# 🩺 Smart Face-Recognition Based Medication Dispenser

**(Raspberry Pi Ready – Laptop Simulation Supported)**

---

## 📌 Project Overview

This project is a **face-recognition-based automated medication dispenser** designed for patient safety.
It identifies patients using face recognition, checks their medication schedule, and dispenses pills **only when allowed**.

Currently:

- ✅ Face recognition is stable
- ✅ Medication scheduling works
- ✅ Dispensing is **simulated on laptop**
- 🔜 Real hardware dispensing via Raspberry Pi (servo motors)

---

## 🧠 System Architecture

```
Camera → Face Recognition → Patient Identification
        → Medication Scheduler → Dispense Decision
        → Dispenser (Simulation / Servo)
        → Logs & Dashboard (future)
```

---

## 🖥️ Current Mode (Laptop / Simulation)

- Face recognition runs on laptop webcam
- Medication dispensing is **simulated** via console logs
- No hardware required

Example output:

```
[SIMULATION] Dispensing from compartment 1
[SIMULATION] Dispense complete
```

---

## 🍓 Raspberry Pi Deployment Guide (IMPORTANT)

This section explains **exactly what needs to change** to move from laptop → Raspberry Pi.

---

# 🔧 Raspberry Pi Hardware Requirements

| Component                | Quantity  |
| ------------------------ | --------- |
| Raspberry Pi 3B / 4      | 1         |
| Servo Motor (SG90)       | 3         |
| External 5V Power Supply | 1         |
| Jumper Wires             | As needed |
| Camera (Pi Cam / USB)    | 1         |

---

# 🎛️ GPIO Pin Mapping (Recommended)

| Compartment | GPIO Pin |
| ----------- | -------- |
| 1           | GPIO 17  |
| 2           | GPIO 27  |
| 3           | GPIO 22  |

---

# 📦 Raspberry Pi Software Setup

### 1️⃣ Install OS

- Raspberry Pi OS (64-bit recommended)
- Enable Camera Interface

```bash
sudo raspi-config
# Interface Options → Camera → Enable
```

---

### 2️⃣ Install Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-opencv -y
pip3 install numpy insightface onnxruntime gpiozero
```

---

### 3️⃣ Camera Check

```bash
libcamera-hello
```

If camera works, face recognition will work.

---

# 🔄 Code Changes Required for Raspberry Pi

### ⚠️ IMPORTANT

**Face recognition logic does NOT change.**
Only the dispenser backend changes.

---

## ✅ 1. Update `medication/dispenser.py`

### 🔁 CURRENT (Laptop Simulation)

```python
SIMULATION_MODE = True
```

### 🔁 CHANGE ON RASPBERRY PI

```python
SIMULATION_MODE = False
```

---

### 🧩 Full Raspberry Pi Servo Implementation

```python
from gpiozero import Servo
from time import sleep

SERVOS = {
    1: Servo(17),
    2: Servo(27),
    3: Servo(22)
}

def servo_dispense(compartment):
    servo = SERVOS.get(compartment)
    if not servo:
        print("[ERROR] Invalid compartment")
        return

    servo.min()
    sleep(0.5)

    servo.max()   # dispense
    sleep(1.0)

    servo.min()
    sleep(0.5)

    print(f"[HARDWARE] Dispensed from compartment {compartment}")
```

---

## ✅ 2. Camera Performance Tweaks (Recommended)

In `face/recognize.py`:

```python
PROCESS_EVERY_N = 4
RESIZE_SCALE = 0.45
```

This improves FPS on Raspberry Pi.

---

## ✅ 3. Safety Features (Already Implemented)

✔ Face confirmation time
✔ Cooldown after dispense
✔ No dispense on:

- multiple faces
- wrong time
- uncertain recognition
  ✔ Dispense lock per patient

---

# 🧪 Testing Checklist (Before Demo)

- [ ] Register patient
- [ ] Add medication schedule
- [ ] Try early → NOT TIME
- [ ] Try correct time → DISPENSED
- [ ] Try again → WAIT Xs
- [ ] Try two people → MULTIPLE FACES

---

# 📊 Future Enhancements (Phase-3)

- Web Dashboard (Flask)
- Logs & analytics
- Alert system (Telegram / Email)
- Mobile app integration
- Cloud sync (optional)

---

# 🏁 Final Notes

- System is designed with **medical safety first**
- All face data stored **locally**
- No cloud biometric storage
- Raspberry Pi ready with minimal code changes

---

## 👨‍💻 Author

Smart Medication Dispenser – Final Year Project
Face Recognition + Embedded Systems + Healthcare Automation

---

If you want next, I can:

- ✔ Add **inline comments for examiners**
- ✔ Create **system diagrams**
- ✔ Write **Methodology & Implementation chapters**
- ✔ Help with **FYP viva questions**

Just tell me what you want next 👌
