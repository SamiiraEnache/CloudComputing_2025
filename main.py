import http.server
import json
import sqlite3
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

def init_db():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT CHECK(gender IN ('Masculin', 'Feminin')) NOT NULL,
            cnp TEXT UNIQUE NOT NULL,
            medical_history TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            experience INTEGER NOT NULL,
            notes TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_time TEXT NOT NULL,
            notes TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    ''')

    conn.commit()
    conn.close()


class HospitalAPIHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _parse_path(self):
        path_parts = self.path.strip('/').split('/')
        if len(path_parts) == 1:
            if path_parts[0] in ["patients", "doctors", "appointments"]:
                return (path_parts[0], None, None)
            return (None, None, None)

        if len(path_parts) == 3:
            resource = path_parts[0]
            search_type = path_parts[1]
            value = path_parts[2]

            if resource == "patients":
                if search_type == "id" and value.isdigit():
                    return ("patients", "id", int(value))
                elif search_type == "cnp":
                    return ("patients", "cnp", value)

            if resource == "doctors":
                if search_type == "id" and value.isdigit():
                    return ("doctors", "id", int(value))
                elif search_type == "department":
                    return ("doctors", "department", value)

            if resource == "appointments":
                if search_type == "id" and value.isdigit():
                    return ("appointments", "id", int(value))
                elif search_type in ["patient", "doctor"] and value.isdigit():
                    return ("appointments", search_type, int(value))

            return (None, None, None)
        return (None, None, None)

    def do_GET(self):
        try:
            resource, search_type, search_value = self._parse_path()
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()

            if resource == "patients":
                if search_type is None:
                    cursor.execute("SELECT * FROM patients")
                    rows = cursor.fetchall()
                    patients = [
                        {
                            "id": row[0],
                            "name": row[1],
                            "age": row[2],
                            "gender": row[3],
                            "cnp": row[4],
                            "medical_history": json.loads(row[5])
                        } for row in rows
                    ]
                    self._set_headers(200)
                    self.wfile.write(json.dumps(patients).encode())
                else:
                    if search_type == "id":
                        cursor.execute("SELECT * FROM patients WHERE id = ?", (search_value,))
                    else:
                        cursor.execute("SELECT * FROM patients WHERE cnp = ?", (search_value,))

                    row = cursor.fetchone()
                    if row:
                        patient = {
                            "id": row[0],
                            "name": row[1],
                            "age": row[2],
                            "gender": row[3],
                            "cnp": row[4],
                            "medical_history": json.loads(row[5])
                        }
                        self._set_headers(200)
                        self.wfile.write(json.dumps(patient).encode())
                    else:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "patient doesn't exist"}).encode())

            elif resource == "doctors":
                if search_type is None:
                    cursor.execute("SELECT * FROM doctors")
                    rows = cursor.fetchall()
                    doctors = [
                        {
                            "id": row[0],
                            "name": row[1],
                            "department": row[2],
                            "experience": row[3],
                            "notes": json.loads(row[4])
                        } for row in rows
                    ]
                    self._set_headers(200)
                    self.wfile.write(json.dumps(doctors).encode())
                else:
                    if search_type == "id":
                        cursor.execute("SELECT * FROM doctors WHERE id = ?", (search_value,))
                        row = cursor.fetchone()
                        if row:
                            doctor = {
                                "id": row[0],
                                "name": row[1],
                                "department": row[2],
                                "experience": row[3],
                                "notes": json.loads(row[4])
                            }
                            self._set_headers(200)
                            self.wfile.write(json.dumps(doctor).encode())
                        else:
                            self._set_headers(404)
                            self.wfile.write(json.dumps({"error": "doctor doesn't exist"}).encode())
                    elif search_type == "department":
                        cursor.execute("SELECT * FROM doctors WHERE department = ?", (search_value,))
                        rows = cursor.fetchall()
                        doctors = [
                            {
                                "id": row[0],
                                "name": row[1],
                                "department": row[2],
                                "experience": row[3],
                                "notes": json.loads(row[4])
                            } for row in rows
                        ]
                        self._set_headers(200)
                        self.wfile.write(json.dumps(doctors).encode())
                    else:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "resource not found"}).encode())

            elif resource == "appointments":
                if search_type is None:
                    cursor.execute("SELECT * FROM appointments")
                    rows = cursor.fetchall()
                    appointments = [
                        {
                            "id": row[0],
                            "patient_id": row[1],
                            "doctor_id": row[2],
                            "appointment_time": row[3],
                            "notes": row[4]
                        } for row in rows
                    ]
                    self._set_headers(200)
                    self.wfile.write(json.dumps(appointments).encode())
                else:
                    if search_type == "id":
                        cursor.execute("SELECT * FROM appointments WHERE id = ?", (search_value,))
                        row = cursor.fetchone()
                        if row:
                            appointment = {
                                "id": row[0],
                                "patient_id": row[1],
                                "doctor_id": row[2],
                                "appointment_time": row[3],
                                "notes": row[4]
                            }
                            self._set_headers(200)
                            self.wfile.write(json.dumps(appointment).encode())
                        else:
                            self._set_headers(404)
                            self.wfile.write(json.dumps({"error": "appointment not found"}).encode())
                    elif search_type in ["patient", "doctor"]:
                        field = "patient_id" if search_type == "patient" else "doctor_id"
                        cursor.execute(f"SELECT * FROM appointments WHERE {field} = ?", (search_value,))
                        rows = cursor.fetchall()
                        appointments = [
                            {
                                "id": row[0],
                                "patient_id": row[1],
                                "doctor_id": row[2],
                                "appointment_time": row[3],
                                "notes": row[4]
                            } for row in rows
                        ]
                        self._set_headers(200)
                        self.wfile.write(json.dumps(appointments).encode())
                    else:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "resource not found"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "resource not found"}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": "internal server error",
                "details": str(e)
            }).encode())
        finally:
            conn.close()

    def do_POST(self):
        try:
            resource, search_type, _ = self._parse_path()
            if resource not in ["patients", "doctors", "appointments"]:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "resource not found"}).encode())
                return
            elif search_type is not None:
                self._set_headers(405)
                self.wfile.write(json.dumps({"error": "method not allowed"}).encode())
                return

            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode())
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()

            if resource == "patients":
                required_fields = {"name", "age", "gender", "cnp", "medical_history"}
                if not required_fields.issubset(post_data.keys()):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "all fields (name, age, gender, cnp, medical_history) are required"
                    }).encode())
                    return

                if post_data["gender"] not in {"Masculin", "Feminin"}:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "must be 'Masculin' or 'Feminin'."}).encode())
                    return

                if not is_valid_cnp(post_data["cnp"]):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "CNP must be exactly 13 digits"
                    }).encode())
                    return

                if not isinstance(post_data["medical_history"], list):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "medical history must be a list"
                    }).encode())
                    return

                cursor.execute("SELECT id FROM patients WHERE cnp = ?", (post_data["cnp"],))
                if cursor.fetchone():
                    self._set_headers(409)
                    self.wfile.write(json.dumps({"error": "CNP already exists"}).encode())
                    return

                cursor.execute(
                    "INSERT INTO patients (name, age, gender, cnp, medical_history) VALUES (?, ?, ?, ?, ?)",
                    (
                        post_data["name"],
                        post_data["age"],
                        post_data["gender"],
                        post_data["cnp"],
                        json.dumps(post_data["medical_history"])
                    )
                )
                conn.commit()
                post_data["id"] = cursor.lastrowid
                self._set_headers(201)
                self.wfile.write(json.dumps(post_data).encode())

            elif resource == "doctors":
                required_fields = {"name", "department", "experience", "notes"}
                if not required_fields.issubset(post_data.keys()):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "all fields (name, department, experience, notes) are required"
                    }).encode())
                    return

                if not is_valid_experience(post_data["experience"]):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "experience must be positive integer"
                    }).encode())
                    return

                if not is_valid_notes(post_data["notes"]):
                    post_data["notes"] = []

                cursor.execute(
                    "INSERT INTO doctors (name, department, experience, notes) VALUES (?, ?, ?, ?)",
                    (
                        post_data["name"],
                        post_data["department"],
                        post_data["experience"],
                        json.dumps(post_data["notes"])
                    )
                )
                conn.commit()
                post_data["id"] = cursor.lastrowid
                self._set_headers(201)
                self.wfile.write(json.dumps(post_data).encode())

            elif resource == "appointments":
                required_fields = {"patient_id", "doctor_id", "appointment_time", "notes"}
                if not required_fields.issubset(post_data.keys()):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "all fields (patient_id, doctor_id, appointment_time, notes) are required"
                    }).encode())
                    return

                if "id" in post_data:
                    del post_data["id"]

                if not (is_valid_id(post_data["patient_id"]) and is_valid_id(post_data["doctor_id"])):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "invalid patient_id or doctor_id cause they should be positive"
                    }).encode())
                    return

                if not is_valid_datetime(post_data["appointment_time"]):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "date must be 'YYYY-MM-DD HH:MM:SS'."
                    }).encode())
                    return

                cursor.execute("SELECT id FROM patients WHERE id = ?", (post_data["patient_id"],))
                if not cursor.fetchone():
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "patient doesn't exist"}).encode())
                    return

                cursor.execute("SELECT id FROM doctors WHERE id = ?", (post_data["doctor_id"],))
                if not cursor.fetchone():
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "doctor doesn't exist"}).encode())
                    return

                cursor.execute("""
                    SELECT id FROM appointments
                    WHERE doctor_id = ?
                      AND appointment_time > datetime(?, '-30 minutes')
                      AND appointment_time < datetime(?, '+30 minutes')
                """, (post_data["doctor_id"], post_data["appointment_time"], post_data["appointment_time"]))
                if cursor.fetchone():
                    self._set_headers(409)
                    self.wfile.write(json.dumps({
                        "error": "doctor has another appointment by this time"
                    }).encode())
                    return

                cursor.execute("""
                    SELECT id FROM appointments
                    WHERE patient_id = ?
                      AND appointment_time > datetime(?, '-30 minutes')
                      AND appointment_time < datetime(?, '+30 minutes')
                """, (post_data["patient_id"], post_data["appointment_time"], post_data["appointment_time"]))
                if cursor.fetchone():
                    self._set_headers(409)
                    self.wfile.write(json.dumps({
                        "error": "patient has another appointment by this time"
                    }).encode())
                    return

                cursor.execute(
                    "INSERT INTO appointments (patient_id, doctor_id, appointment_time, notes) VALUES (?, ?, ?, ?)",
                    (
                        post_data["patient_id"],
                        post_data["doctor_id"],
                        post_data["appointment_time"],
                        post_data["notes"]
                    )
                )
                conn.commit()
                post_data["id"] = cursor.lastrowid
                self._set_headers(201)
                self.wfile.write(json.dumps(post_data).encode())

            conn.close()

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": "internal server error",
                "details": str(e)
            }).encode())

    def do_PUT(self):
        try:
            resource, search_type, search_value = self._parse_path()
            if resource not in ["patients", "doctors", "appointments"]:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "resource not found"}).encode())
                return
            elif search_type is None:
                self._set_headers(405)
                self.wfile.write(json.dumps({"error": "method not allowed"}).encode())
                return
            elif search_type != "id":
                self._set_headers(405)
                self.wfile.write(json.dumps({"error": "method not allowed"}).encode())
                return

            content_length = int(self.headers['Content-Length'])
            put_data = json.loads(self.rfile.read(content_length).decode())

            if "id" in put_data and put_data["id"] != search_value:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": "ID doesn t match URL id"
                }).encode())
                return

            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()

            if resource == "patients":
                required_fields = {"name", "age", "gender", "cnp", "medical_history"}
                if not required_fields.issubset(put_data.keys()):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "all fields (name, age, gender, cnp, medical_history) are required"
                    }).encode())
                    conn.close()
                    return

                if not isinstance(put_data["medical_history"], list):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "medical history must be a list"
                    }).encode())
                    conn.close()
                    return

                if not is_valid_cnp(put_data["cnp"]):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "CNP must be exactly 13 digits"
                    }).encode())
                    conn.close()
                    return

                cursor.execute("SELECT * FROM patients WHERE id = ?", (search_value,))
                existing_patient = cursor.fetchone()
                if not existing_patient:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "patient doesn't exist"}).encode())
                    conn.close()
                    return

                old_cnp = existing_patient[4]
                if put_data["cnp"] != old_cnp:
                    cursor.execute("SELECT id FROM patients WHERE cnp = ? AND id != ?", (put_data["cnp"], search_value))
                    if cursor.fetchone():
                        self._set_headers(409)
                        self.wfile.write(json.dumps({
                            "error": "CNP already exists for another patient"
                        }).encode())
                        conn.close()
                        return

                cursor.execute("""
                    UPDATE patients
                    SET name = ?, age = ?, gender = ?, cnp = ?, medical_history = ?
                    WHERE id = ?
                """, (
                    put_data["name"],
                    put_data["age"],
                    put_data["gender"],
                    put_data["cnp"],
                    json.dumps(put_data["medical_history"]),
                    search_value
                ))
                conn.commit()
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "message": "patient updated successfully",
                    "updated_data": put_data
                }).encode())

            elif resource == "doctors":
                required_fields = {"name", "department", "experience", "notes"}
                if not required_fields.issubset(put_data.keys()):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "all fields are required"}).encode())
                    conn.close()
                    return

                if not is_valid_experience(put_data["experience"]):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "experience must be positive"}).encode())
                    conn.close()
                    return

                if not is_valid_notes(put_data["notes"]):
                    put_data["notes"] = []

                cursor.execute("SELECT * FROM doctors WHERE id = ?", (search_value,))
                if not cursor.fetchone():
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "doctor doesn't exist"}).encode())
                    conn.close()
                    return

                cursor.execute("""
                    UPDATE doctors
                    SET name = ?, department = ?, experience = ?, notes = ?
                    WHERE id = ?
                """, (
                    put_data["name"],
                    put_data["department"],
                    put_data["experience"],
                    json.dumps(put_data["notes"]),
                    search_value
                ))
                conn.commit()
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "message": "doctor updated successfully",
                    "updated_data": put_data
                }).encode())

            elif resource == "appointments":
                required_fields = {"patient_id", "doctor_id", "appointment_time", "notes"}
                if not required_fields.issubset(put_data.keys()):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "all fields (patient_id, doctor_id, appointment_time, notes) are required"
                    }).encode())
                    conn.close()
                    return

                if not (is_valid_id(put_data["patient_id"]) and is_valid_id(put_data["doctor_id"])):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "patient_id or doctor_id must be positive"
                    }).encode())
                    conn.close()
                    return

                if not is_valid_datetime(put_data["appointment_time"]):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "error": "date must be 'YYYY-MM-DD HH:MM:SS'"
                    }).encode())
                    conn.close()
                    return

                cursor.execute("SELECT * FROM appointments WHERE id = ?", (search_value,))
                existing_appointment = cursor.fetchone()
                if not existing_appointment:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "appointment not found"}).encode())
                    conn.close()
                    return

                old_patient_id = existing_appointment[1]
                old_doctor_id = existing_appointment[2]
                old_datetime = existing_appointment[3]

                doctor_changed = (put_data["doctor_id"] != old_doctor_id)
                patient_changed = (put_data["patient_id"] != old_patient_id)
                time_changed = (put_data["appointment_time"] != old_datetime)

                cursor.execute("SELECT id FROM patients WHERE id = ?", (put_data["patient_id"],))
                if not cursor.fetchone():
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "patient doesn't exist"}).encode())
                    conn.close()
                    return

                cursor.execute("SELECT id FROM doctors WHERE id = ?", (put_data["doctor_id"],))
                if not cursor.fetchone():
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "doctor doesn't exist"}).encode())
                    conn.close()
                    return

                if doctor_changed or patient_changed or time_changed:
                    cursor.execute("""
                        SELECT id FROM appointments
                        WHERE doctor_id = ?
                          AND appointment_time > datetime(?, '-30 minutes')
                          AND appointment_time < datetime(?, '+30 minutes')
                          AND id != ?
                    """, (
                        put_data["doctor_id"],
                        put_data["appointment_time"],
                        put_data["appointment_time"],
                        search_value
                    ))
                    if cursor.fetchone():
                        self._set_headers(409)
                        self.wfile.write(json.dumps({
                            "error": "doctor has another appointment by this time"
                        }).encode())
                        conn.close()
                        return

                    cursor.execute("""
                        SELECT id FROM appointments
                        WHERE patient_id = ?
                          AND appointment_time > datetime(?, '-30 minutes')
                          AND appointment_time < datetime(?, '+30 minutes')
                          AND id != ?
                    """, (
                        put_data["patient_id"],
                        put_data["appointment_time"],
                        put_data["appointment_time"],
                        search_value
                    ))
                    if cursor.fetchone():
                        self._set_headers(409)
                        self.wfile.write(json.dumps({
                            "error": "patient has another appointment by this time"
                        }).encode())
                        conn.close()
                        return

                cursor.execute("""
                    UPDATE appointments
                    SET patient_id = ?, doctor_id = ?, appointment_time = ?, notes = ?
                    WHERE id = ?
                """, (
                    put_data["patient_id"],
                    put_data["doctor_id"],
                    put_data["appointment_time"],
                    put_data["notes"],
                    search_value
                ))
                conn.commit()
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "message": "appointment updated successfully",
                    "updated_data": put_data
                }).encode())

            conn.close()

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": "internal server error",
                "details": str(e)
            }).encode())

    def do_DELETE(self):
        try:
            resource, search_type, search_value = self._parse_path()
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()

            if resource == "patients" and search_type in {"id", "cnp"}:
                if search_type == "id":
                    cursor.execute("SELECT id FROM patients WHERE id = ?", (search_value,))
                else:
                    cursor.execute("SELECT id FROM patients WHERE cnp = ?", (search_value,))

                row = cursor.fetchone()
                if not row:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "patient not found"}).encode())
                    conn.close()
                    return

                pid = row[0]
                cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (pid,))
                cursor.execute("DELETE FROM patients WHERE id = ?", (pid,))
                conn.commit()
                self._set_headers(204)
                self.wfile.write(b"")

            elif resource == "doctors":
                if search_type == "id":
                    cursor.execute("SELECT id FROM doctors WHERE id = ?", (search_value,))
                    row = cursor.fetchone()
                    if not row:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "doctor doesn't exist"}).encode())
                        conn.close()
                        return

                    doc_id = row[0]
                    cursor.execute("DELETE FROM appointments WHERE doctor_id = ?", (doc_id,))
                    cursor.execute("DELETE FROM doctors WHERE id = ?", (doc_id,))
                    conn.commit()
                    self._set_headers(204)
                    self.wfile.write(b"")

                elif search_type == "department":
                    if self.headers.get("X-Admin") != "true":
                        self._set_headers(403)
                        self.wfile.write(json.dumps({
                            "error": "unauthorized"
                        }).encode())
                        conn.close()
                        return

                    cursor.execute("SELECT id FROM doctors WHERE department = ?", (search_value,))
                    docs_found = cursor.fetchall()
                    if not docs_found:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "no doctors found in that department"}).encode())
                        conn.close()
                        return

                    for d in docs_found:
                        doc_id = d[0]
                        cursor.execute("DELETE FROM appointments WHERE doctor_id = ?", (doc_id,))

                    cursor.execute("DELETE FROM doctors WHERE department = ?", (search_value,))
                    conn.commit()
                    self._set_headers(204)
                    self.wfile.write(b"")
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "resource not found"}).encode())

            elif resource == "appointments" and search_type == "id":
                cursor.execute("SELECT * FROM appointments WHERE id = ?", (search_value,))
                if not cursor.fetchone():
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "appointment not found"}).encode())
                    conn.close()
                    return

                cursor.execute("DELETE FROM appointments WHERE id = ?", (search_value,))
                conn.commit()
                self._set_headers(204)
                self.wfile.write(b"")

            elif resource in ["patients", "doctors", "appointments"] and search_type is None:
                self._set_headers(405)
                self.wfile.write(json.dumps({"error": "method not allowed"}).encode())

            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "resource not found"}).encode())

            conn.close()

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": "internal server error",
                "details": str(e)
            }).encode())


if __name__ == "__main__":
    init_db()
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, HospitalAPIHandler)
    print("Starting server!")
    httpd.serve_forever()
