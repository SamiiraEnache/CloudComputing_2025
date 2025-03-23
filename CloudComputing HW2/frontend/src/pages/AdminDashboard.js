import React, { useEffect, useState } from "react";
import axios from "axios";

const AdminDashboard = () => {
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [formVisible, setFormVisible] = useState(false);
  const [formMode, setFormMode] = useState("create");
  const [formData, setFormData] = useState({
    id: null,
    name: "",
    department: "",
    experience: "",
    notes: "",
  });
  const [filterDept, setFilterDept] = useState("");
  const [error, setError] = useState("");
  const [countryInfo, setCountryInfo] = useState({});

  const fetchDoctors = async () => {
    try {
      const res = await axios.get("/doctors");
      const docs = res.data.doctors;
      setDoctors(docs);
      setFilteredDoctors(docs);

      docs.forEach(async (doc) => {
        const nameParts = doc.name.toLowerCase().split(" ");
        const suspectedName = nameParts[0];
        try {
          const countryRes = await axios.get(`https://restcountries.com/v3.1/name/${suspectedName}?fullText=false`);
          const country = countryRes.data[0];
          setCountryInfo((prev) => ({
            ...prev,
            [doc.id]: {
              flag: country.flags?.svg,
              languages: Object.values(country.languages || {}).join(", "),
              countryName: country.name?.common,
            },
          }));
        } catch {
        }
      });
    } catch {
      setError("Eroare la preluare");
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  const handleDelete = (id) => {
    if (!window.confirm("Sigur?")) return;

    axios
      .delete(`/doctors/id/${id}`)
      .then(() => fetchDoctors())
      .catch(() => alert("Eroare la ștergere"));
  };

  const handleMassDelete = () => {
    if (!filterDept) {
      alert("Selecteaza un departament");
      return;
    }
    if (!window.confirm(`Stergi toti doctorii din ${filterDept}?`)) return;

    axios
      .delete(`/doctors/department/${filterDept}`, {
        headers: { "X-Admin": "true" },
      })
      .then(() => {
        setFilterDept("");
        fetchDoctors();
      })
      .catch(() => alert("Eroare"));
  };

  const handleEdit = (doc) => {
    setFormMode("edit");
    setFormVisible(true);
    setFormData({
      id: doc.id,
      name: doc.name,
      department: doc.department,
      experience: doc.experience,
      notes: Array.isArray(doc.notes) ? doc.notes.join(", ") : doc.notes,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      name: formData.name,
      department: formData.department,
      experience: parseInt(formData.experience),
      notes: formData.notes
        .split(",")
        .map((n) => n.trim())
        .filter((n) => n !== ""),
    };

    try {
      if (formMode === "create") {
        await axios.post("/doctors", payload);
      } else {
        await axios.put(`/doctors/id/${formData.id}`, {
          ...payload,
          id: formData.id,
        });
      }
      fetchDoctors();
      setFormVisible(false);
      setFormData({ id: null, name: "", department: "", experience: "", notes: "" });
    } catch {
      alert("Eroare");
    }
  };

  const applyFilter = () => {
    if (!filterDept) return;
    const result = doctors.filter((doc) => doc.department === filterDept);
    setFilteredDoctors(result);
  };

  const resetFilter = () => {
    setFilterDept("");
    setFilteredDoctors(doctors);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 p-6">
      <div className="max-w-6xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
        <h1 className="text-3xl font-bold text-blue-700 mb-6">Admin Dashboard</h1>

        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <select
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
            className="border px-3 py-2 rounded-lg"
          >
            <option value="">-- Filtreaza dupa dep --</option>
            {[...new Set(doctors.map((d) => d.department))].map((dep) => (
              <option key={dep} value={dep}>{dep}</option>
            ))}
          </select>

          <button
            onClick={applyFilter}
            className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
          >
            Aplica filtrul
          </button>

          <button
            onClick={resetFilter}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
          >
            Reseteaza
          </button>

          <button
            onClick={handleMassDelete}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
          >
            Sterge departamentul
          </button>

          <button
            onClick={() => {
              setFormMode("create");
              setFormVisible(true);
              setFormData({ id: null, name: "", department: "", experience: "", notes: "" });
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            + Adauga doctor
          </button>
        </div>

        {error && <div className="text-red-600 font-semibold mb-4">{error}</div>}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredDoctors.map((doc) => (
            <div
              key={doc.id}
              className="bg-blue-50 border border-blue-200 p-4 rounded-xl shadow"
            >
              <h3 className="text-xl font-semibold">{doc.name}</h3>
              <p className="text-sm text-gray-700">Departament: {doc.department}</p>
              <p className="text-sm text-gray-700">Experiență: {doc.experience} ani</p>
              <p className="font-medium mt-2">Note:</p>
              <ul className="list-disc list-inside text-sm text-gray-700">
                {Array.isArray(doc.notes) ? doc.notes.map((n, i) => <li key={i}>{n}</li>) : <li>{doc.notes}</li>}
              </ul>

              {countryInfo[doc.id] && (
                <div className="mt-3 p-3 bg-white border rounded-xl shadow-inner">
                  <p className="text-sm font-medium">Țară detectată: {countryInfo[doc.id].countryName}</p>
                  <p className="text-sm text-gray-600">Limbi: {countryInfo[doc.id].languages}</p>
                  {countryInfo[doc.id].flag && (
                    <img src={countryInfo[doc.id].flag} alt="Steag" className="w-12 mt-1" />
                  )}
                </div>
              )}

              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => handleEdit(doc)}
                  className="bg-purple-500 text-white px-3 py-1 rounded-lg text-sm hover:bg-purple-600"
                >
                  Editeaza
                </button>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="bg-red-500 text-white px-3 py-1 rounded-lg text-sm hover:bg-red-600"
                >
                  Sterge
                </button>
              </div>
            </div>
          ))}
        </div>

        {formVisible && (
          <form onSubmit={handleSubmit} className="mt-8 bg-white border rounded-xl p-6 shadow">
            <h2 className="text-xl font-bold mb-4">
              {formMode === "create" ? "Adauga" : "Editeaza"} doctor
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Nume"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="border px-3 py-2 rounded-lg"
                required
              />
              <input
                type="text"
                placeholder="Departament"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                className="border px-3 py-2 rounded-lg"
                required
              />
              <input
                type="number"
                placeholder="Experienta (ani)"
                value={formData.experience}
                onChange={(e) => setFormData({ ...formData, experience: e.target.value })}
                className="border px-3 py-2 rounded-lg"
                min="0"
                required
              />
              <input
                type="text"
                placeholder="Note"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="border px-3 py-2 rounded-lg"
              />
            </div>

            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setFormVisible(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg"
              >
                Anuleaza
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {formMode === "create" ? "Creează" : "Salvează"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
