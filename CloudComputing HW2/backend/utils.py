import re
from datetime import datetime

def is_valid_datetime(dt):
    try:
        datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

def is_valid_experience(exp):
    return isinstance(exp, int) and exp >= 0

def is_valid_cnp(cnp):
    return bool(re.fullmatch(r"\d{13}", cnp))

def is_valid_notes(notes):
    return isinstance(notes, list)

def is_valid_id(id_val):
    return isinstance(id_val, int) and id_val > 0

def build_patient_links(patient_id):
    return {
        "self": {
            "href": f"/patients/id/{patient_id}",
            "method": "GET"
        },
        "update": {
            "href": f"/patients/id/{patient_id}",
            "method": "PUT"
        },
        "delete": {
            "href": f"/patients/id/{patient_id}",
            "method": "DELETE"
        }
    }

def build_doctor_links(doctor_id):
    return {
        "self": {
            "href": f"/doctors/id/{doctor_id}",
            "method": "GET"
        },
        "update": {
            "href": f"/doctors/id/{doctor_id}",
            "method": "PUT"
        },
        "delete": {
            "href": f"/doctors/id/{doctor_id}",
            "method": "DELETE"
        }
    }

def build_appointment_links(appointment_id):
    return {
        "self": {
            "href": f"/appointments/id/{appointment_id}",
            "method": "GET"
        },
        "update": {
            "href": f"/appointments/id/{appointment_id}",
            "method": "PUT"
        },
        "delete": {
            "href": f"/appointments/id/{appointment_id}",
            "method": "DELETE"
        }
    }
