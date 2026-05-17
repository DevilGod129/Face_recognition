import serial
import time

# 🔥 CHANGE THIS if needed
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

time.sleep(2)  # allow connection to settle

print("Connected to Arduino")

while True:
    if arduino.in_waiting:
        msg = arduino.readline().decode().strip()
        print("Received:", msg)

        # 🧠 When robot stops
        if msg == "STOP":
            print("Checkpoint detected")

            time.sleep(2)

            # 🔥 Send command to Arduino
            arduino.write(b'd1\n')

        # 🧠 After dispensing
        elif msg == "DONE":
            print("Dispense finished")

            time.sleep(1)

            arduino.write(b'go\n')
