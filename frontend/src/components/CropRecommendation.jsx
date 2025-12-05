import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/CropRecommendation.css";

function CropRecommendation() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    N: "",
    P: "",
    K: "",
    temperature: "",
    humidity: "",
    ph: "",
    rainfall: "",
  });
  const [recommendations, setRecommendations] = useState([]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:5000/api/crop-recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error("Error fetching prediction:", err);
    }
  };

  const placeholders = {
    N: "Enter Nitrogen content (N) in soil",
    P: "Enter Phosphorus content (P) in soil",
    K: "Enter Potassium content (K) in soil",
    temperature: "Enter temperature in °C",
    humidity: "Enter humidity (%)",
    ph: "Enter soil pH value (0–14)",
    rainfall: "Enter rainfall (mm)",
  };

  return (
    <div className="crop-container">
      

      <h2>🌾 Crop Recommendation</h2>
      <p className="desc">
        Enter your soil and environmental parameters to get AI-based crop recommendations.
      </p>

      <form onSubmit={handleSubmit} className="form-box">
        {Object.keys(formData).map((key) => (
          <div className="input-group" key={key}>
            <label>{key.toUpperCase()}</label>
            <input
              type="number"
              name={key}
              placeholder={placeholders[key]}
              value={formData[key]}
              onChange={handleChange}
              required
            />
          </div>
        ))}
        <button type="submit" className="predict-btn">
          🚜 Predict Crop
        </button>
      </form>

      {recommendations.length > 0 && (
        <div className="result">
          <h3>🌱 Top 3 Recommended Crops</h3>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {recommendations.map((rec, idx) => (
              <li key={idx}>
                <strong>{rec.crop}</strong> — Confidence:{" "}
                {rec.confidence.toFixed(2)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default CropRecommendation;
