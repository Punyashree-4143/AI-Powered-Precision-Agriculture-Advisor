// src/pages/DiseasePredictor.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/DiseasePredictor.css";

// MAIN backend base URL from env
const API_BASE = process.env.REACT_APP_API_BASE;

if (!API_BASE) {
  console.error("❌ VITE_API_BASE is not defined in environment variables");
}

export default function DiseasePredictor() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ------------------- CLEANUP PREVIEW URL -------------------
  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  // ------------------- HANDLERS -------------------
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

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

    if (!API_BASE) {
      setError("Backend URL not configured");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("image", image);

    try {
      const res = await axios.post(
        `${API_BASE}/disease-predict`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 20000,
        }
      );

      setResult(res.data);
    } catch (err) {
      console.error("Disease prediction error:", err);
      setError(
        err.response?.data?.error ||
        "Prediction failed. Please try again later."
      );
    } finally {
      setLoading(false);
    }
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

            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />

            {preview && (
              <img
                src={preview}
                alt="preview"
                className="dp-preview"
              />
            )}

            <button
              className="dp-button"
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? "Predicting…" : "Predict"}
            </button>

            {error && <p className="dp-error">{error}</p>}
          </div>

          {/* RIGHT PANEL */}
          <div className="dp-right">
            <p className="dp-heading">Prediction Result</p>

            {!result && !loading && (
              <p className="dp-placeholder">
                Result will appear here…
              </p>
            )}

            {result && (
              <div className="dp-result">
                <p><strong>🌿 Crop:</strong> {result.crop}</p>
                <p><strong>🦠 Disease:</strong> {result.disease}</p>
                <p><strong>📊 Confidence:</strong> {result.confidence}%</p>

                <p className="dp-subTitle">Organic Treatment</p>
                <ul className="dp-list">
                  {result.treatment?.organic?.length
                    ? result.treatment.organic.map((t, idx) => (
                        <li key={idx}>{t}</li>
                      ))
                    : <li>No data available</li>}
                </ul>

                <p className="dp-subTitle">Chemical Treatment</p>
                <ul className="dp-list">
                  {result.treatment?.chemical?.length
                    ? result.treatment.chemical.map((t, idx) => (
                        <li key={idx}>{t}</li>
                      ))
                    : <li>No data available</li>}
                </ul>

                <p className="dp-subTitle">Prevention</p>
                <ul className="dp-list">
                  {result.treatment?.prevention?.length
                    ? result.treatment.prevention.map((t, idx) => (
                        <li key={idx}>{t}</li>
                      ))
                    : <li>No data available</li>}
                </ul>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
