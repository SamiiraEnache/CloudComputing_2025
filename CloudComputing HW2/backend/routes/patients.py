from flask import Blueprint, request, jsonify
import json

from backend.database import get_connection
from backend.utils import (
    is_valid_cnp,
    is_valid_id,
    build_patient_links
)

patients_bp = Blueprint("patients", __name__)

@patients_bp.route("/patients", methods=["GET"])
def get_all_patients():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        rows = cursor.fetchall()

        patients = []
        for row in rows:
            p = {
                "id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "cnp": row[4],
                "medical_history": json.loads(row[5]),
                "links": build_patient_links(row[0])
            }
            patients.append(p)

        response_data = {
            "patients": patients,
            "_links": {
                "self": {"href": "/patients", "method": "GET"},
                "create": {"href": "/patients", "method": "POST"}
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@patients_bp.route("/patients", methods=["POST"])
def create_patient():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON"}), 400

        required_fields = {"name", "age", "gender", "cnp", "medical_history"}
        if not required_fields.issubset(data.keys()):
            return jsonify({"error": "all fields (name, age, gender, cnp, medical_history) are required"}), 400

        if data["gender"] not in {"Masculin", "Feminin"}:
            return jsonify({"error": "gender must be 'Masculin' or 'Feminin'."}), 400

        if not is_valid_cnp(data["cnp"]):
            return jsonify({"error": "CNP must be exactly 13 digits"}), 400

        if not isinstance(data["medical_history"], list):
            return jsonify({"error": "medical history must be a list"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM patients WHERE cnp = ?", (data["cnp"],))
        if cursor.fetchone():
            return jsonify({"error": "CNP already exists"}), 409

        cursor.execute("""
            INSERT INTO patients (name, age, gender, cnp, medical_history)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["age"],
            data["gender"],
            data["cnp"],
            json.dumps(data["medical_history"])
        ))
        conn.commit()

        new_id = cursor.lastrowid
        data["id"] = new_id
        data["links"] = build_patient_links(new_id)

        return jsonify(data), 201

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@patients_bp.route("/patients/id/<int:patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    if not is_valid_id(patient_id):
        return jsonify({"error": "Invalid patient ID"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()

        if row:
            patient = {
                "id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "cnp": row[4],
                "medical_history": json.loads(row[5]),
                "links": build_patient_links(row[0])
            }
            return jsonify(patient), 200
        else:
            return jsonify({"error": "patient doesn't exist"}), 404

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@patients_bp.route("/patients/id/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    if not is_valid_id(patient_id):
        return jsonify({"error": "Invalid patient ID"}), 400

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON"}), 400

        required_fields = {"name", "age", "gender", "cnp", "medical_history"}
        if not required_fields.issubset(data.keys()):
            return jsonify({"error": "all fields (name, age, gender, cnp, medical_history) are required"}), 400

        if not isinstance(data["medical_history"], list):
            return jsonify({"error": "medical history must be a list"}), 400

        if not is_valid_cnp(data["cnp"]):
            return jsonify({"error": "CNP must be exactly 13 digits"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        existing_patient = cursor.fetchone()
        if not existing_patient:
            return jsonify({"error": "patient doesn't exist"}), 404

        old_cnp = existing_patient[4]
        if data["cnp"] != old_cnp:
            cursor.execute("SELECT id FROM patients WHERE cnp = ? AND id != ?", (data["cnp"], patient_id))
            if cursor.fetchone():
                return jsonify({"error": "CNP already exists for another patient"}), 409

        cursor.execute("""
            UPDATE patients
            SET name = ?, age = ?, gender = ?, cnp = ?, medical_history = ?
            WHERE id = ?
        """, (
            data["name"],
            data["age"],
            data["gender"],
            data["cnp"],
            json.dumps(data["medical_history"]),
            patient_id
        ))
        conn.commit()

        data["id"] = patient_id
        data["links"] = build_patient_links(patient_id)

        return jsonify({"message": "patient updated successfully", "updated_data": data}), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@patients_bp.route("/patients/id/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    if not is_valid_id(patient_id):
        return jsonify({"error": "Invalid patient ID"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "patient not found"}), 404

        pid = row[0]
        cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (pid,))
        cursor.execute("DELETE FROM patients WHERE id = ?", (pid,))
        conn.commit()

        return "", 204

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()
