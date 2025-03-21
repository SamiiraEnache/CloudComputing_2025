from flask import Blueprint, request, jsonify
import json

from backend.database import get_connection
from backend.utils import (
    is_valid_id,
    is_valid_experience,
    is_valid_notes,
    build_doctor_links
)

doctors_bp = Blueprint("doctors", __name__)

@doctors_bp.route("/doctors", methods=["GET"])
def get_all_doctors():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors")
        rows = cursor.fetchall()

        doctors = []
        for row in rows:
            d = {
                "id": row[0],
                "name": row[1],
                "department": row[2],
                "experience": row[3],
                "notes": json.loads(row[4]),
                "links": build_doctor_links(row[0])
            }
            doctors.append(d)

        response_data = {
            "doctors": doctors,
            "_links": {
                "self": {"href": "/doctors", "method": "GET"},
                "create": {"href": "/doctors", "method": "POST"}
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@doctors_bp.route("/doctors", methods=["POST"])
def create_doctor():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON"}), 400

        required_fields = {"name", "department", "experience", "notes"}
        if not required_fields.issubset(data.keys()):
            return jsonify({"error": "all fields (name, department, experience, notes) are required"}), 400

        if not is_valid_experience(data["experience"]):
            return jsonify({"error": "experience must be a non-negative integer"}), 400

        if not is_valid_notes(data["notes"]):
            data["notes"] = []

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO doctors (name, department, experience, notes)
            VALUES (?, ?, ?, ?)
        """, (
            data["name"],
            data["department"],
            data["experience"],
            json.dumps(data["notes"])
        ))
        conn.commit()

        new_id = cursor.lastrowid
        data["id"] = new_id
        data["links"] = build_doctor_links(new_id)

        return jsonify(data), 201

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@doctors_bp.route("/doctors/id/<int:doctor_id>", methods=["GET"])
def get_doctor_by_id(doctor_id):
    if not is_valid_id(doctor_id):
        return jsonify({"error": "Invalid doctor ID"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        row = cursor.fetchone()

        if row:
            doctor = {
                "id": row[0],
                "name": row[1],
                "department": row[2],
                "experience": row[3],
                "notes": json.loads(row[4]),
                "links": build_doctor_links(row[0])
            }
            return jsonify(doctor), 200
        else:
            return jsonify({"error": "doctor doesn't exist"}), 404

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@doctors_bp.route("/doctors/id/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    if not is_valid_id(doctor_id):
        return jsonify({"error": "Invalid doctor ID"}), 400

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON"}), 400

        if "id" in data and data["id"] != doctor_id:
            return jsonify({"error": "ID doesn't match URL id"}), 400

        required_fields = {"name", "department", "experience", "notes"}
        if not required_fields.issubset(data.keys()):
            return jsonify({"error": "all fields are required"}), 400

        if not is_valid_experience(data["experience"]):
            return jsonify({"error": "experience must be non-negative"}), 400

        if not is_valid_notes(data["notes"]):
            data["notes"] = []

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        if not cursor.fetchone():
            return jsonify({"error": "doctor doesn't exist"}), 404

        cursor.execute("""
            UPDATE doctors
            SET name = ?, department = ?, experience = ?, notes = ?
            WHERE id = ?
        """, (
            data["name"],
            data["department"],
            data["experience"],
            json.dumps(data["notes"]),
            doctor_id
        ))
        conn.commit()

        data["id"] = doctor_id
        data["links"] = build_doctor_links(doctor_id)

        return jsonify({"message": "doctor updated successfully", "updated_data": data}), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@doctors_bp.route("/doctors/id/<int:doctor_id>", methods=["DELETE"])
def delete_doctor_by_id(doctor_id):
    if not is_valid_id(doctor_id):
        return jsonify({"error": "Invalid doctor ID"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM doctors WHERE id = ?", (doctor_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "doctor doesn't exist"}), 404

        doc_id = row[0]
        cursor.execute("DELETE FROM appointments WHERE doctor_id = ?", (doc_id,))
        cursor.execute("DELETE FROM doctors WHERE id = ?", (doc_id,))
        conn.commit()

        return "", 204

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@doctors_bp.route("/doctors/department/<department>", methods=["GET"])
def get_doctors_by_department(department):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE department = ?", (department,))
        rows = cursor.fetchall()

        doctors = []
        for row in rows:
            d = {
                "id": row[0],
                "name": row[1],
                "department": row[2],
                "experience": row[3],
                "notes": json.loads(row[4]),
                "links": build_doctor_links(row[0])
            }
            doctors.append(d)

        if not doctors:
            return jsonify({"error": "no doctors found in that department"}), 404

        return jsonify(doctors), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()

@doctors_bp.route("/doctors/department/<department>", methods=["DELETE"])
def delete_doctors_by_department(department):
    try:
        if request.headers.get("X-Admin") != "true":
            return jsonify({"error": "unauthorized"}), 403

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM doctors WHERE department = ?", (department,))
        docs_found = cursor.fetchall()
        if not docs_found:
            return jsonify({"error": "no doctors found in that department"}), 404

        for d in docs_found:
            doc_id = d[0]
            cursor.execute("DELETE FROM appointments WHERE doctor_id = ?", (doc_id,))

        cursor.execute("DELETE FROM doctors WHERE department = ?", (department,))
        conn.commit()

        return "", 204

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
    finally:
        conn.close()
