import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [role, setRole] = useState("doctor");
  const [username, setUsername] = useState(""); // doar pentru admin
  const [password, setPassword] = useState("");
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("/doctors")
      .then((response) => {
        const doctorsList = response.data.doctors || [];
        setDoctors(doctorsList);
      })
      .catch((err) => {
        console.error("Eroare la fetch doctors:", err);
        setDoctors([]);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (role === "admin") {
      if (!username || !password) {
        setError("Completeaza tot");
        return;
      }

      if (username === "admin" && password === "admin123") {
        navigate("/admin");
      } else {
        setError("Date incorecte");
      }
    } else {
      // doctor login
      if (!selectedDoctorId || !password) {
        setError("Selecteaza un medic si introdu parola");
        return;
      }

      if (password !== "medic123") {
        setError("Parola incorectă pentru medic.");
        return;
      }

      navigate(`/doctor/${selectedDoctorId}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-white flex items-center justify-center px-4">
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-md p-8 relative transition-all">
        <h2 className="text-3xl font-bold text-center text-blue-700 mb-6">
          SAMIVA
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* roles */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">
              Rolul utilizatorului:
            </label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => {
                  setRole("doctor");
                  setError("");
                }}
                className={`w-1/2 py-2 rounded-xl font-semibold transition-all ${
                  role === "doctor"
                    ? "bg-blue-600 text-white shadow-md"
                    : "bg-gray-100 text-gray-700"
                }`}
              >
                Doctor
              </button>
              <button
                type="button"
                onClick={() => {
                  setRole("admin");
                  setError("");
                }}
                className={`w-1/2 py-2 rounded-xl font-semibold transition-all ${
                  role === "admin"
                    ? "bg-blue-600 text-white shadow-md"
                    : "bg-gray-100 text-gray-700"
                }`}
              >
                Admin
              </button>
            </div>
          </div>

          {/* admin */}
          {role === "admin" && (
            <>
              <div>
                <label className="block text-gray-700 font-medium mb-1">
                  Utilizator:
                </label>
                <input
                  type="text"
                  placeholder="ex: admin"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">
                  Parola:
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
            </>
          )}

          {/* doctor */}
          {role === "doctor" && (
            <>
              <div>
                <label className="block text-gray-700 font-medium mb-1">
                  Selecteaza medicul:
                </label>
                <select
                  onChange={(e) => setSelectedDoctorId(e.target.value)}
                  className="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-300"
                >
                  <option value="">Alege un medic</option>
                  {doctors.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">
                  Parola:
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
            </>
          )}

          {error && (
            <div className="text-red-600 font-medium text-sm">{error}</div>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-xl shadow-md transition-all duration-200"
          >
            Conecteaza-te
          </button>
        </form>

        <div className="absolute top-2 right-3 text-xs text-gray-400">
          CC • 2025
        </div>
      </div>
    </div>
  );
};

export default Login;
