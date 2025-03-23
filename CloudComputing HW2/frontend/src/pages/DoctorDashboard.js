import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";

const DoctorDashboard = () => {
  const { id } = useParams();

  const [doctor, setDoctor] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [selectedView, setSelectedView] = useState("appointments");
  const [error, setError] = useState("");

  const [formMode, setFormMode] = useState("create");
  const [formVisible, setFormVisible] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    patient_id: "",
    appointment_time: "",
    notes: [],
  });
  const [notesInput, setNotesInput] = useState("");

  const [filterPatientId, setFilterPatientId] = useState("");

  const [medQuery, setMedQuery] = useState("");
  const [medInfo, setMedInfo] = useState(null);
  const [medLoading, setMedLoading] = useState(false);
  const [medError, setMedError] = useState("");

  const [weatherLocation, setWeatherLocation] = useState("");
  const [weatherForecast, setWeatherForecast] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState("");

  const [patientModalVisible, setPatientModalVisible] = useState(false);
  const [patientFormData, setPatientFormData] = useState({
    name: "",
    age: "",
    gender: "",
    cnp: "",
    medical_history: [],
  });
  const [medicalHistoryInput, setMedicalHistoryInput] = useState("");
  const [patientFormError, setPatientFormError] = useState("");

  const fetchAppointments = () => {
    axios
      .get(`/appointments/doctor/${id}`)
      .then((res) => {
        setAppointments(res.data);
        setFilteredAppointments(res.data);
      })
      .catch(() => setError("Eroare la preluarea programari"));
  };

  const fetchPatients = () => {
    axios
      .get("/patients")
      .then((res) => setPatients(res.data.patients || []))
      .catch(() => setError("Eroare la preluarea pacienti"));
  };

  const searchMedication = async () => {
    if (!medQuery) return;
    setMedLoading(true);
    setMedError("");
    setMedInfo(null);
    try {
      const res = await axios.get(
        `https://api.fda.gov/drug/label.json?search=openfda.generic_name:${medQuery}&limit=1`
      );
      const result = res.data.results[0];
      setMedInfo({
        name: result.openfda.brand_name?.[0] || "N/A",
        purpose: result.purpose?.[0] || "Informatie indisponibila",
        usage: result.indications_and_usage?.[0] || "N/A",
        warnings: result.warnings?.[0] || "N/A",
      });
    } catch (error) {
      setMedError("Medicamentul nu a fost gasit sau a aparut o eroare");
    } finally {
      setMedLoading(false);
    }
  };

  const fetchWeatherForecast = async () => {
    if (!weatherLocation.trim()) return;
    setWeatherLoading(true);
    setWeatherError("");
    setWeatherForecast(null);
    try {
      const API_KEY = "22ec0130a9564e18b7c121353252303";
      const url = `https://api.weatherapi.com/v1/forecast.json?key=${API_KEY}&q=${encodeURIComponent(
        weatherLocation
      )}&days=11`;
      const response = await axios.get(url);
      setWeatherForecast(response.data);
    } catch (err) {
      setWeatherError("Nu s-a putut prelua");
    } finally {
      setWeatherLoading(false);
    }
  };

  useEffect(() => {
    axios
      .get(`/doctors/id/${id}`)
      .then((res) => setDoctor(res.data))
      .catch(() => setError("Eroare la preluarea datelor doctorului"));
    fetchAppointments();
    fetchPatients();
  }, [id]);

  const handleDeleteAppointment = (appointmentId) => {
    if (!window.confirm("Sigur?")) return;
    axios
      .delete(`/appointments/id/${appointmentId}`)
      .then(() => fetchAppointments())
      .catch(() => alert("Eroare la ștergerea programarii"));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formData.patient_id || !formData.appointment_time) {
      alert("Completeaza toate campurile");
      return;
    }
    try {
      const payload = {
        patient_id: parseInt(formData.patient_id),
        doctor_id: parseInt(id),
        appointment_time: dayjs(formData.appointment_time).format("YYYY-MM-DD HH:mm:ss"),
        notes: notesInput
          .split(",")
          .map((note) => note.trim())
          .filter((note) => note !== ""),
      };
      if (formMode === "create") {
        await axios.post("/appointments", payload);
      } else {
        await axios.put(`/appointments/id/${formData.id}`, payload);
      }
      fetchAppointments();
      setFormVisible(false);
      setFormData({ id: null, patient_id: "", appointment_time: "", notes: [] });
      setNotesInput("");
    } catch (err) {
      alert("Eroare la salvarea programarii");
    }
  };

  const handleEdit = (appt) => {
    setFormMode("edit");
    setFormVisible(true);
    setFormData({
      id: appt.id,
      patient_id: appt.patient_id,
      appointment_time: appt.appointment_time,
      notes: Array.isArray(appt.notes) ? appt.notes : [appt.notes],
    });
    setNotesInput(Array.isArray(appt.notes) ? appt.notes.join(", ") : appt.notes);
  };

  const getPatientName = (pid) => {
    const patient = patients.find((p) => p.id === pid);
    return patient ? patient.name : "Necunoscut";
  };

  const handleFilterByPatient = () => {
    if (!filterPatientId) return;
    const filtered = appointments.filter((appt) => appt.patient_id === parseInt(filterPatientId));
    setFilteredAppointments(filtered);
  };

  const resetFilter = () => {
    setFilterPatientId("");
    setFilteredAppointments(appointments);
  };

  const handlePatientFormSubmit = async (e) => {
    e.preventDefault();
    setPatientFormError("");

    const { name, age, gender, cnp } = patientFormData;
    if (!name || !age || !gender || !cnp) {
      setPatientFormError("Toate campurile sunt obligatorii");
      return;
    }
    if (!/^\d{13}$/.test(cnp)) {
      setPatientFormError("CNP-ul trebuie să aiba exact 13 cifre");
      return;
    }

    const payload = {
      name,
      age: parseInt(age),
      gender,
      cnp,
      medical_history: medicalHistoryInput
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item !== ""),
    };

    console.log("Payload being sent:", payload);

    try {
      const response = await axios.post("/patients", payload);
      console.log("API Response:", response.data);
      fetchPatients();
      setPatientModalVisible(false);
      setPatientFormData({ name: "", age: "", gender: "", cnp: "", medical_history: [] });
      setMedicalHistoryInput("");
    } catch (err) {
      console.error("Error adding patient:", err.response?.data || err.message); 
      setPatientFormError(
        err.response?.data?.error || "Eroare la crearea pacientului"
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-200 p-6">
      <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
        <h1 className="text-3xl font-bold text-blue-700 mb-2">
          Bine ai venit, {doctor?.name || "Doctor"}!
        </h1>
        <p className="text-gray-500 mb-6">
          Specialitatea: {doctor?.department} | Experiență: {doctor?.experience} ani
        </p>

        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setSelectedView("appointments")}
            className={`px-4 py-2 rounded-lg ${
              selectedView === "appointments"
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-800"
            }`}
          >
            Programari
          </button>
          <button
            onClick={() => setSelectedView("patients")}
            className={`px-4 py-2 rounded-lg ${
              selectedView === "patients" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-800"
            }`}
          >
            Pacienti
          </button>
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}

        {selectedView === "appointments" && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Programarile tale</h2>
              <button
                onClick={() => {
                  setFormMode("create");
                  setFormVisible(true);
                  setFormData({ id: null, patient_id: "", appointment_time: "", notes: [] });
                  setNotesInput("");
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-purple-700"
              >
                + Adauga programare
              </button>
            </div>

            <div className="mb-4 flex flex-col md:flex-row gap-3">
              <select
                className="border px-3 py-2 rounded-lg"
                value={filterPatientId}
                onChange={(e) => setFilterPatientId(e.target.value)}
              >
                <option value="">-- Filtreaza după pacient --</option>
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
              <button
                onClick={handleFilterByPatient}
                className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
              >
                Filtreaza
              </button>
              <button
                onClick={resetFilter}
                className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
              >
                Reseteaza
              </button>
            </div>

            <div className="mb-6 mt-4">
              <h3 className="text-lg font-semibold mb-2">Cauta informatii despre un medicament</h3>
              <div className="flex gap-2 flex-col md:flex-row">
                <input
                  type="text"
                  value={medQuery}
                  onChange={(e) => setMedQuery(e.target.value)}
                  placeholder="ex: ibuprofen"
                  className="border px-3 py-2 rounded-lg w-full md:w-1/3"
                />
                <button
                  onClick={searchMedication}
                  className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
                >
                  Cauta
                </button>
              </div>
              {medLoading && <p className="text-sm text-gray-500 mt-2">Se caută...</p>}
              {medError && <p className="text-red-500 text-sm mt-2">{medError}</p>}
              {medInfo && (
                <div className="mt-4 bg-purple-50 border border-purple-200 p-4 rounded-xl shadow">
                  <h4 className="text-lg font-bold text-purple-700 mb-2">{medInfo.name}</h4>
                  <p>
                    <strong>Scop:</strong> {medInfo.purpose}
                  </p>
                  <p className="mt-2">
                    <strong>Utilizare:</strong> {medInfo.usage}
                  </p>
                  <p className="mt-2">
                    <strong>Avertismente:</strong> {medInfo.warnings}
                  </p>
                </div>
              )}
            </div>

            <div className="mb-6 mt-4 bg-white p-4 rounded-xl shadow">
              <h3 className="text-lg font-semibold mb-4">Verifica prognoza meteo pentru programari</h3>
              <div className="flex flex-col md:flex-row gap-2 mb-2">
                <input
                  type="text"
                  className="border px-3 py-2 rounded-lg w-full md:w-1/3"
                  placeholder="ex: Iasi obvy"
                  value={weatherLocation}
                  onChange={(e) => setWeatherLocation(e.target.value)}
                />
                <button
                  onClick={fetchWeatherForecast}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Afiseaza prognoza
                </button>
              </div>
              {weatherLoading && <p className="text-sm text-gray-500">Se încarcă prognoza...</p>}
              {weatherError && <p className="text-red-500 text-sm">{weatherError}</p>}
              {weatherForecast && (
                <div className="mt-4 border border-gray-200 p-4 rounded-lg">
                  <h4 className="text-lg font-bold mb-2">
                    {weatherForecast.location.name}, {weatherForecast.location.country}
                  </h4>
                  <p className="text-gray-700 mb-2">
                    <strong>Ultima actualizare:</strong> {weatherForecast.current.last_updated}
                  </p>
                  <div className="flex items-center mb-4">
                    <img
                      src={weatherForecast.current.condition.icon}
                      alt="condiții meteo"
                      className="mr-2"
                    />
                    <span className="text-xl">
                      {weatherForecast.current.temp_c}°C, {weatherForecast.current.condition.text}
                    </span>
                  </div>
                  <div className="grid md:grid-cols-3 gap-4">
                    {weatherForecast.forecast.forecastday.map((day) => (
                      <div key={day.date} className="bg-blue-50 p-3 rounded-lg shadow">
                        <p className="font-bold text-gray-800">{day.date}</p>
                        <div className="flex items-center my-2">
                          <img src={day.day.condition.icon} alt="condiții" className="mr-2" />
                          <span>{day.day.condition.text}</span>
                        </div>
                        <p>
                          <strong>Max:</strong> {day.day.maxtemp_c}°C,
                          <strong> Min:</strong> {day.day.mintemp_c}°C
                        </p>
                        <p>
                          <strong>Sanse de ploaie:</strong> {day.day.daily_chance_of_rain}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {filteredAppointments.length === 0 ? (
              <p className="text-gray-500">Nu ai programari.</p>
            ) : (
              <div className="space-y-4">
                {filteredAppointments.map((appt) => (
                  <div
                    key={appt.id}
                    className="bg-blue-50 border border-blue-200 p-4 rounded-xl shadow relative"
                  >
                    <p>
                      <strong>Pacient:</strong> {getPatientName(appt.patient_id)}
                    </p>
                    <p>
                      <strong>Data:</strong> {appt.appointment_time}
                    </p>
                    <p>
                      <strong>Note:</strong>
                    </p>
                    <ul className="list-disc list-inside text-sm text-gray-700">
                      {Array.isArray(appt.notes) ? (
                        appt.notes.map((n, i) => <li key={i}>{n}</li>)
                      ) : (
                        <li>{appt.notes}</li>
                      )}
                    </ul>
                    <div className="absolute top-2 right-2 flex gap-2">
                      <button
                        onClick={() => handleEdit(appt)}
                        className="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded-lg text-sm"
                      >
                        Editeaza
                      </button>
                      <button
                        onClick={() => handleDeleteAppointment(appt.id)}
                        className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm"
                      >
                        Sterge
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {formVisible && (
              <form onSubmit={handleFormSubmit} className="mt-6 bg-white border rounded-xl p-4 shadow">
                <h3 className="text-lg font-bold mb-4">
                  {formMode === "create" ? "Adauga" : "Editeaza"} programare
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block mb-1 text-sm font-medium text-gray-700">Pacient:</label>
                    <select
                      className="w-full border px-3 py-2 rounded-lg"
                      value={formData.patient_id}
                      onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                      required
                    >
                      <option value="">-- Alege --</option>
                      {patients.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1 text-sm font-medium text-gray-700">Data & ora:</label>
                    <input
                      type="datetime-local"
                      value={dayjs(formData.appointment_time).format("YYYY-MM-DDTHH:mm")}
                      onChange={(e) => setFormData({ ...formData, appointment_time: e.target.value })}
                      className="w-full border px-3 py-2 rounded-lg"
                      required
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block mb-1 text-sm font-medium text-gray-700">Note:</label>
                  <input
                    type="text"
                    value={notesInput}
                    onChange={(e) => setNotesInput(e.target.value)}
                    className="w-full border px-3 py-2 rounded-lg"
                    placeholder="ex: tensiune mare"
                  />
                </div>
                <div className="mt-4 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setFormVisible(false)}
                    className="px-4 py-2 rounded-lg border border-gray-300"
                  >
                    Anuleaza
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
                  >
                    {formMode === "create" ? "Creeaza" : "Salveaza"}
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {selectedView === "patients" && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Pacientii tai</h2>
              <button
                onClick={() => setPatientModalVisible(true)}
                className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg shadow-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
              >
                + Adauga Pacient Nou
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {patients
                .filter((p) => appointments.some((a) => a.patient_id === p.id))
                .map((patient) => (
                  <div
                    key={patient.id}
                    className="bg-purple-50 border border-purple-200 p-4 rounded-xl shadow"
                  >
                    <h3 className="text-lg font-semibold">{patient.name}</h3>
                    <p className="text-sm">CNP: {patient.cnp}</p>
                    <p className="text-sm">Varsta: {patient.age} ani</p>
                    <p className="text-sm">Gen: {patient.gender}</p>
                    <p className="mt-2 font-medium">Istoric medical:</p>
                    <ul className="list-disc list-inside text-sm text-gray-700">
                      {patient.medical_history.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
            </div>
          </div>
        )}

        {patientModalVisible && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-3xl p-8 w-full max-w-md shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-purple-500 to-pink-500"></div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Adaugă un pacient nou</h3>
              {patientFormError && <p className="text-red-500 text-sm mb-4">{patientFormError}</p>}
              <form onSubmit={handlePatientFormSubmit}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Nume</label>
                    <input
                      type="text"
                      value={patientFormData.name}
                      onChange={(e) =>
                        setPatientFormData({ ...patientFormData, name: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      placeholder="ex: Ion Popescu"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Vârsta</label>
                    <input
                      type="number"
                      value={patientFormData.age}
                      onChange={(e) =>
                        setPatientFormData({ ...patientFormData, age: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      placeholder="ex: 45"
                      min="0"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Gen</label>
                    <select
                      value={patientFormData.gender}
                      onChange={(e) =>
                        setPatientFormData({ ...patientFormData, gender: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                    >
                      <option value="">-- Selectează --</option>
                      <option value="Masculin">Masculin</option>
                      <option value="Feminin">Feminin</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">CNP</label>
                    <input
                      type="text"
                      value={patientFormData.cnp}
                      onChange={(e) =>
                        setPatientFormData({ ...patientFormData, cnp: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      placeholder="ex: 1234567890123"
                      maxLength="13"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Istoric medical (separă prin virgulă)
                    </label>
                    <textarea
                      value={medicalHistoryInput}
                      onChange={(e) => setMedicalHistoryInput(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      placeholder="ex: Diabet, Hipertensiune"
                      rows="3"
                    />
                  </div>
                </div>
                <div className="mt-6 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setPatientModalVisible(false);
                      setPatientFormError("");
                    }}
                    className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-all"
                  >
                    Anulează
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all shadow-md"
                  >
                    Creează Pacient
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DoctorDashboard;
