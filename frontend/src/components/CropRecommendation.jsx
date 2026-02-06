import React, { useState } from "react";
import "../styles/CropRecommendation.css";

const CROP_API_BASE = process.env.REACT_APP_CROP_API;

if (!CROP_API_BASE) {
  console.error("❌ REACT_APP_CROP_API is missing. Check .env or Vercel env vars.");
}

function CropRecommendation() {
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
      const res = await fetch(`${CROP_API_BASE}/crop-recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error("Crop recommendation error:", err);
    }
  };

  return (
    <div className="crop-container">
      <h2>🌾 Crop Recommendation</h2>

      <form onSubmit={handleSubmit} className="form-box">
        <div className="crop-grid">
          {Object.keys(formData).map((key) => (
            <div className="input-group" key={key}>
              <label>{key.toUpperCase()}</label>
              <input
                type="number"
                name={key}
                value={formData[key]}
                onChange={handleChange}
                required
              />
            </div>
          ))}
        </div>

        <button type="submit" className="predict-btn">
          🚜 Predict Crop
        </button>
      </form>

      {recommendations.length > 0 && (
        <div className="result-box">
          <h3>🌱 Top Recommended Crops</h3>

          <div className="result-horizontal">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="result-card">
                <p>{rec.crop}</p>
                <small>{rec.confidence}%</small>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CropRecommendation;
