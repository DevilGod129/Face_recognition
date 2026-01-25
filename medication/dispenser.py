import time

# Change this later on Raspberry Pi
SIMULATION_MODE = True


def dispense_medication(compartment):
    if SIMULATION_MODE:
        simulate_dispense(compartment)
    else:
        servo_dispense(compartment)


def simulate_dispense(compartment):
    print(f"[SIMULATION] Dispensing from compartment {compartment}")
    time.sleep(1)
    print("[SIMULATION] Dispense complete")


def servo_dispense(compartment):
    # This will be implemented on Raspberry Pi
    raise NotImplementedError("Servo control not yet implemented")
