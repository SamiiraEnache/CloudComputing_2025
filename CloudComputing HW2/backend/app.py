
from flask import Flask
from database import init_db
from routes.patients import patients_bp
from routes.doctors import doctors_bp
from routes.appointments import appointments_bp

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def home():
        return {
            "message": "API is running! Check /patients, /doctors, /appointments"
        }, 200

    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)

    return app

if __name__ == "__main__":
    init_db()

    app = create_app()
    print("Flask server startingggg")
    app.run(host="0.0.0.0", port=8080, debug=True)
