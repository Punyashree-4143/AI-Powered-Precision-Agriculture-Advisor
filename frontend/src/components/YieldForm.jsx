import React, { useState } from "react";
import "../styles/yield.css";
import { predictYield } from "../api/yieldApi";

export default function YieldForm({ onResult }) {
  const [form, setForm] = useState({
    District: "",
    Crop: "",
    Soil_Type: "",
    Year: "",
    Area_acre: "",
    Annual_Rainfall_mm: "",
    Avg_Temp_C: "",
    Irrigation_Index: "",
    Fertilizer_kg_per_ha: "",
    Pesticide_kg_per_ha: "",
    Production_tonnes: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await predictYield(form);
    onResult(response);
  } catch (err) {
    onResult({ status: "error", message: "Server error" });
  }
};


  const placeholders = {
    District: "Enter district name",
    Crop: "Enter crop name",
    Soil_Type: "Enter soil type",
    Year: "Enter year (e.g., 2023)",
    Area_acre: "Enter cultivated area (acre)",
    Annual_Rainfall_mm: "Enter total annual rainfall (mm)",
    Avg_Temp_C: "Enter average temperature (°C)",
    Irrigation_Index: "Enter irrigation index",
    Fertilizer_kg_per_ha: "Enter fertilizer used per ha",
    Pesticide_kg_per_ha: "Enter pesticide used per ha",
    Production_tonnes: "Enter total production (tonnes)",
  };

  return (
    <div className="yield-container">

      <h2>🌾 Yield Prediction</h2>
      <p className="yield-desc">
        Enter all necessary agricultural parameters to predict expected yield using AI.
      </p>


      <form onSubmit={handleSubmit} className="yield-form-box">
  <div className="yield-grid">
    {Object.keys(form).map((key) => (
      <div className="yield-input-group" key={key}>
        <label>{key.replace(/_/g, " ")}</label>
        <input
          type="text"
          name={key}
          placeholder={placeholders[key]}
          value={form[key]}
          onChange={handleChange}
          required
        />
      </div>
    ))}
  </div>

  <button type="submit" className="yield-btn">
    🌱 Predict Yield
  </button>
</form>

      
    </div>
  );
}
