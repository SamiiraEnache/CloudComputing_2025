from flask import Flask
from flask_cors import CORS

from backend.routes.doctors import doctors_bp
from backend.routes.patients import patients_bp
from backend.routes.appointments import appointments_bp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.register_blueprint(doctors_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(appointments_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
