// src/components/IrrigationForm.jsx
import { useState } from "react";

const IrrigationForm = ({ onSubmit }) => {
  const [form, setForm] = useState({
    crop: "",
    state: "Karnataka",
    district: "",
    soil_type: "Loamy",
  });

  const states = ["Karnataka"];
  const districts = [
    "Bagalkote","Mandya","Mysore","Davanagere","Hassan","Belagavi",
    "Tumakuru","Raichur","Vijayapura","Koppal"
  ];
  const crops = ["Sugarcane","Paddy","Wheat","Cotton","Maize"];
  const soils = ["Loamy", "Sandy", "Clay"];

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-xl shadow-md space-y-4"
    >
      <h2 className="text-xl font-semibold text-gray-700">
        🌧️ Irrigation Planner
      </h2>

      <div>
        <label className="font-medium">Crop</label>
        <select
          name="crop"
          onChange={handleChange}
          className="w-full mt-1 p-2 border rounded"
        >
          <option value="">Select Crop</option>
          {crops.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="font-medium">State</label>
        <select
          name="state"
          onChange={handleChange}
          className="w-full mt-1 p-2 border rounded"
        >
          {states.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="font-medium">District</label>
        <select
          name="district"
          onChange={handleChange}
          className="w-full mt-1 p-2 border rounded"
        >
          <option value="">Select District</option>
          {districts.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="font-medium">Soil Type</label>
        <select
          name="soil_type"
          onChange={handleChange}
          className="w-full mt-1 p-2 border rounded"
        >
          {soils.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <button
        className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
      >
        Get Irrigation Plan
      </button>
    </form>
  );
};

export default IrrigationForm;
