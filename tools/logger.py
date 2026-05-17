import requests

# Backend API endpoint
LOG_API = "http://192.168.137.1:8000/api/logs"
API_KEY = "supersecretkey123"


def log_event(patient_id, patient_name, status, compartment=None, confidence=None):
    try:
        payload = {
            "status": status,
            "compartment": int(compartment) if compartment else 0,
            "confidence": float(confidence) if confidence else 0.0,
            "patient_id": int(patient_id)
        }

        headers = {
            "x-api-key": API_KEY
        }

        response = requests.post(LOG_API, json=payload, headers=headers)

        print("[LOG] Sent to backend:", response.status_code)

    except Exception as e:
        print("[LOG ERROR]", e)

