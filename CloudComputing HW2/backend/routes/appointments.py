from flask import Blueprint, request, jsonify

from backend.database import get_connection
from backend.utils import (
    is_valid_id,
    is_valid_datetime,
    is_valid_notes,
    build_appointment_links
)

appointments_bp = Blueprint("appointments", __name__)

@appointments_bp.route("/appointments", methods=["GET"])
def get_all_appointments():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments")
        rows = cursor.fetchall()

        appointments = []
        for row in rows:
            a = {
                "id": row[0],
                "patient_id": row[1],
                "doctor_id": row[2],
                "appointment_time": row[3],
                "notes": row[4],
                "links": build_appointment_links(row[0])
            }
            appointments.append(a)

        response_data = {
            "appointments": appointments,
            "_links": {
                "self": {"href": "/appointments", "method": "GET"},
                "create": {"href": "/appointments", "method": "POST"}
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()


@appointments_bp.route("/appointments", methods=["POST"])
def create_appointment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON"}), 400

        required_fields = {"patient_id", "doctor_id", "appointment_time", "notes"}
        if not required_fields.issubset(data.keys()):
            return jsonify({
                "error": "all fields (patient_id, doctor_id, appointment_time, notes) are required"
            }), 400

        if not (is_valid_id(data["patient_id"]) and is_valid_id(data["doctor_id"])):
            return jsonify({"error": "invalid patient_id or doctor_id, both should be positive"}), 400

        if not is_valid_datetime(data["appointment_time"]):
            return jsonify({"error": "date must be 'YYYY-MM-DD HH:MM:SS'."}), 400

        if not is_valid_notes(data["notes"]):
            return jsonify({"error": "notes must be a list"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Verificăm existența pacientului
        cursor.execute("SELECT id FROM patients WHERE id = ?", (data["patient_id"],))
        if not cursor.fetchone():
            return jsonify({"error": "patient doesn't exist"}), 404

        # Verificăm existența doctorului
        cursor.execute("SELECT id FROM doctors WHERE id = ?", (data["doctor_id"],))
        if not cursor.fetchone():
            return jsonify({"error": "doctor doesn't exist"}), 404

        # Verificăm programările pentru doctor (±30 min)
        cursor.execute("""
            SELECT id FROM appointments
            WHERE doctor_id = ?
              AND appointment_time > datetime(?, '-30 minutes')
              AND appointment_time < datetime(?, '+30 minutes')
        """, (data["doctor_id"], data["appointment_time"], data["appointment_time"]))
        if cursor.fetchone():
            return jsonify({"error": "doctor has another appointment at this time"}), 409

        # Verificăm programările pentru pacient (±30 min)
        cursor.execute("""
            SELECT id FROM appointments
            WHERE patient_id = ?
              AND appointment_time > datetime(?, '-30 minutes')
              AND appointment_time < datetime(?, '+30 minutes')
        """, (data["patient_id"], data["appointment_time"], data["appointment_time"]))
        if cursor.fetchone():
            return jsonify({"error": "patient has another appointment at this time"}), 409

        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_time, notes)
            VALUES (?, ?, ?, ?)
        """, (
            data["patient_id"],
            data["doctor_id"],
            data["appointment_time"],
            data["notes"]
        ))
        conn.commit()

        new_id = cursor.lastrowid
        data["id"] = new_id
        data["links"] = build_appointment_links(new_id)

        return jsonify(data), 201

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@appointments_bp.route("/appointments/id/<int:appointment_id>", methods=["GET"])
def get_appointment_by_id(appointment_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        row = cursor.fetchone()

        if row:
            appointment = {
                "id": row[0],
                "patient_id": row[1],
                "doctor_id": row[2],
                "appointment_time": row[3],
                "notes": row[4],
                "links": build_appointment_links(row[0])
            }
            return jsonify(appointment), 200
        else:
            return jsonify({"error": "appointment not found"}), 404

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()


@appointments_bp.route("/appointments/patient/<int:patient_id>", methods=["GET"])
def get_appointments_by_patient(patient_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE patient_id = ?", (patient_id,))
        rows = cursor.fetchall()

        appointments = []
        for row in rows:
            a = {
                "id": row[0],
                "patient_id": row[1],
                "doctor_id": row[2],
                "appointment_time": row[3],
                "notes": row[4],
                "links": build_appointment_links(row[0])
            }
            appointments.append(a)

        return jsonify(appointments), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()


@appointments_bp.route("/appointments/doctor/<int:doctor_id>", methods=["GET"])
def get_appointments_by_doctor(doctor_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE doctor_id = ?", (doctor_id,))
        rows = cursor.fetchall()

        appointments = []
        for row in rows:
            a = {
                "id": row[0],
                "patient_id": row[1],
                "doctor_id": row[2],
                "appointment_time": row[3],
                "notes": row[4],
                "links": build_appointment_links(row[0])
            }
            appointments.append(a)

        return jsonify(appointments), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()


@appointments_bp.route("/appointments/id/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON"}), 400

        if "id" in data and data["id"] != appointment_id:
            return jsonify({"error": "ID doesn't match URL id"}), 400

        required_fields = {"patient_id", "doctor_id", "appointment_time", "notes"}
        if not required_fields.issubset(data.keys()):
            return jsonify({
                "error": "all fields (patient_id, doctor_id, appointment_time, notes) are required"
            }), 400

        if not is_valid_id(data["patient_id"]) or not is_valid_id(data["doctor_id"]):
            return jsonify({"error": "patient_id or doctor_id must be positive"}), 400

        if not is_valid_datetime(data["appointment_time"]):
            return jsonify({"error": "date must be 'YYYY-MM-DD HH:MM:SS'"}), 400

        if not is_valid_notes(data["notes"]):
            return jsonify({"error": "notes must be a list"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # verificăm dacă programarea există
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        existing_appointment = cursor.fetchone()
        if not existing_appointment:
            return jsonify({"error": "appointment not found"}), 404

        old_patient_id = existing_appointment[1]
        old_doctor_id = existing_appointment[2]
        old_datetime = existing_appointment[3]

        doctor_changed = (data["doctor_id"] != old_doctor_id)
        patient_changed = (data["patient_id"] != old_patient_id)
        time_changed = (data["appointment_time"] != old_datetime)

        # verificăm existența entităților
        cursor.execute("SELECT id FROM patients WHERE id = ?", (data["patient_id"],))
        if not cursor.fetchone():
            return jsonify({"error": "patient doesn't exist"}), 404

        cursor.execute("SELECT id FROM doctors WHERE id = ?", (data["doctor_id"],))
        if not cursor.fetchone():
            return jsonify({"error": "doctor doesn't exist"}), 404

        # Dacă s-a schimbat doctorul/pacientul/ora, verificăm conflict ±30 min
        if doctor_changed or patient_changed or time_changed:
            cursor.execute("""
                SELECT id FROM appointments
                WHERE doctor_id = ?
                  AND appointment_time > datetime(?, '-30 minutes')
                  AND appointment_time < datetime(?, '+30 minutes')
                  AND id != ?
            """, (
                data["doctor_id"],
                data["appointment_time"],
                data["appointment_time"],
                appointment_id
            ))
            if cursor.fetchone():
                return jsonify({"error": "doctor has another appointment by this time"}), 409

            cursor.execute("""
                SELECT id FROM appointments
                WHERE patient_id = ?
                  AND appointment_time > datetime(?, '-30 minutes')
                  AND appointment_time < datetime(?, '+30 minutes')
                  AND id != ?
            """, (
                data["patient_id"],
                data["appointment_time"],
                data["appointment_time"],
                appointment_id
            ))
            if cursor.fetchone():
                return jsonify({"error": "patient has another appointment by this time"}), 409

        # Facem update
        cursor.execute("""
            UPDATE appointments
            SET patient_id = ?, doctor_id = ?, appointment_time = ?, notes = ?
            WHERE id = ?
        """, (
            data["patient_id"],
            data["doctor_id"],
            data["appointment_time"],
            data["notes"],
            appointment_id
        ))
        conn.commit()

        data["id"] = appointment_id
        data["links"] = build_appointment_links(appointment_id)

        return jsonify({
            "message": "appointment updated successfully",
            "updated_data": data
        }), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()


@appointments_bp.route("/appointments/id/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        if not cursor.fetchone():
            return jsonify({"error": "appointment not found"}), 404

        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()

        return "", 204

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()
