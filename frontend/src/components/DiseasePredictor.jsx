// src/pages/DiseasePredictor.jsx
import React, { useState } from "react";
import axios from "axios";
import "../styles/DiseasePredictor.css";

export default function DiseasePredictor() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ------------------- HANDLERS -------------------
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setError("");
    setResult(null);
  };

  const handlePredict = async () => {
    if (!image) {
      setError("Please upload an image!");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("image", image);

    try {
      const res = await axios.post("http://127.0.0.1:5001/predict", formData);
      setResult(res.data);
    } catch (err) {
      setError("Prediction failed. Try again.");
    }

    setLoading(false);
  };

  // ------------------- UI -------------------
  return (
    <div className="dp-page-content">
      <div className="dp-wrapper">

        <h2 className="dp-title">🌱 Plant Disease Detection</h2>

        <div className="dp-card">

          {/* LEFT PANEL */}
          <div className="dp-left">
            <p className="dp-heading">Upload Image</p>

            <input type="file" accept="image/*" onChange={handleFileChange} />

            {preview && <img src={preview} alt="preview" className="dp-preview" />}

            <button className="dp-button" onClick={handlePredict}>
              {loading ? "Predicting…" : "Predict"}
            </button>

            {error && <p className="dp-error">{error}</p>}
          </div>

          {/* RIGHT PANEL */}
          <div className="dp-right">
            <p className="dp-heading">Prediction Result</p>

            {!result && <p className="dp-placeholder">Result will appear here…</p>}

            {result && (
              <div className="dp-result">
                <p><strong>🌿 Crop:</strong> {result.crop}</p>
                <p><strong>🦠 Disease:</strong> {result.disease}</p>
                <p><strong>📊 Confidence:</strong> {result.confidence}%</p>

                <p className="dp-subTitle">Organic Treatment</p>
                <ul className="dp-list">
                  {result.treatment.organic.map((t, idx) => (
                    <li key={idx}>{t}</li>
                  ))}
                </ul>

                <p className="dp-subTitle">Chemical Treatment</p>
                <ul className="dp-list">
                  {result.treatment.chemical.map((t, idx) => (
                    <li key={idx}>{t}</li>
                  ))}
                </ul>

                <p className="dp-subTitle">Prevention</p>
                <ul className="dp-list">
                  {result.treatment.prevention.map((t, idx) => (
                    <li key={idx}>{t}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
