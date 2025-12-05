// src/pages/IrrigationPlanner.jsx
import React, { useMemo, useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  TimeScale
} from "chart.js";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import "../styles/IrrigationPlanner.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  TimeScale
);

// CONSTANTS
const DISTRICTS_KARNATAKA = [
  "Bagalkote", "Ballari", "Bangalore", "Bangalore Urban", "Bangalore Rural",
  "Chikkaballapur", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad",
  "Gadag", "Kalaburagi", "Hassan", "Haveri", "Kolar", "Kodagu", "Koppal",
  "Mandya", "Mysore", "Raichur", "Shivamogga", "Tumakuru", "Udupi",
  "Uttara Kannada", "Vijayapura", "Yadgir"
];

const CROPS = [
  "Sugarcane", "Paddy", "Maize", "Cotton", "Wheat", "Ragi", "Groundnut",
  "Tur", "Soybean", "Potato", "Onion", "Tomato", "Banana", "Coconut",
  "Pulses", "Sunflower", "Mustard", "Sesame", "Millet", "Barley"
];

const SOIL_TYPES = ["Sandy", "Loamy", "Clay"];

const GROWTH_STAGES = {
  Sugarcane: {
    Tillering: 25,
    Vegetative: 22,
    Maturity: 20,
    Harvesting: 18,
  },
  Paddy: {
    Transplanting: 40,
    "Panicle Initiation": 35,
    Flowering: 32,
    Maturity: 30,
  },
  Maize: {
    Vegetative: 30,
    Tasseling: 28,
    Silking: 26,
    "Grain Filling": 24,
  },
};

const BACKEND = "http://localhost:5000/api/irrigation";

export default function IrrigationPlanner() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    state: "Karnataka",
    district: "Mandya",
    crop: "Sugarcane",
    soil_type: "Loamy",
    growth_stage: "Tillering",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultRef = useRef(null);

  useEffect(() => {
    if (!formData.district) {
      setFormData((f) => ({ ...f, district: DISTRICTS_KARNATAKA[0] }));
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        crop: formData.crop,
        state: formData.state,
        district: formData.district,
        soil_type: formData.soil_type,
      };

      const res = await axios.post(BACKEND, payload, { timeout: 15000 });
      const data = Array.isArray(res.data) ? res.data : res.data.plan || [];

      const threshold =
        GROWTH_STAGES[formData.crop]?.[formData.growth_stage] ?? 20;

      const enriched = data.map((d) => ({
        ...d,
        growth_stage_threshold: threshold
      }));

      setResult(enriched);

      setTimeout(() => {
        if (resultRef.current)
          resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);

    } catch (err) {
      setError(err?.response?.data?.error || "Failed to fetch irrigation plan");
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    if (!result) return null;

    return {
      labels: result.map((r) => r.date),
      datasets: [
        {
          label: "Soil Moisture (%)",
          data: result.map((r) => r.predicted_soil_moisture_percent),
          borderColor: "#2b7cff",
          backgroundColor: "rgba(43,124,255,0.08)",
          tension: 0.3,
          yAxisID: "y1",
          pointRadius: 3,
        },
      ],
    };
  }, [result]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
  };

  const handleExportPDF = async () => {
    if (!resultRef.current) return alert("No results to export");

    try {
      const canvas = await html2canvas(resultRef.current, {
        scale: 2,
        useCORS: true,
      });
      const img = canvas.toDataURL("image/png");
      const pdf = new jsPDF("landscape", "pt", "a4");

      const pdfW = pdf.internal.pageSize.getWidth();
      const pdfH = pdf.internal.pageSize.getHeight();
      const ratio = Math.min(pdfW / canvas.width, pdfH / canvas.height);

      pdf.addImage(img, "PNG", 20, 20, canvas.width * ratio, canvas.height * ratio);
      pdf.save(`irrigation_plan_${formData.district}.pdf`);

    } catch {
      alert("PDF export failed");
    }
  };

  return (
    <div className="page-content">
      <div className="irrigation-wrapper">

        <h2 className="planner-title">Irrigation Planner</h2>

        <form className="panel form" onSubmit={handleSubmit}>
          <div className="form-row">
            
            {/* STATE */}
            <label>
              State
              <select name="state" value={formData.state} onChange={handleChange}>
                <option value="Karnataka">Karnataka</option>
              </select>
            </label>

            {/* DISTRICT */}
            <label>
              District
              <select name="district" value={formData.district} onChange={handleChange}>
                {DISTRICTS_KARNATAKA.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </label>

            {/* CROP */}
            <label>
              Crop
              <select name="crop" value={formData.crop} onChange={handleChange}>
                {CROPS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>

            {/* STAGE */}
            <label>
              Growth Stage
              <select name="growth_stage" value={formData.growth_stage} onChange={handleChange}>
                {Object.keys(GROWTH_STAGES[formData.crop] || {}).map((st) => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </label>

            {/* SOIL TYPE */}
            <label>
              Soil Type
              <select name="soil_type" value={formData.soil_type} onChange={handleChange}>
                {SOIL_TYPES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </label>
          </div>

          {/* BUTTONS */}
          <div className="form-row actions-row">
            <button className="btn primary" type="submit" disabled={loading}>
              {loading ? "Generating..." : "Generate Plan"}
            </button>

            <button className="btn secondary" type="button" onClick={() => setResult(null)}>
              Clear
            </button>

            <button className="btn export" type="button" disabled={!result} onClick={handleExportPDF}>
              Export PDF
            </button>
          </div>
        </form>

        {/* ERROR */}
        {error && <div className="panel error">{error}</div>}

        {/* RESULT */}
        {result && (
          <section className="panel result-section" ref={resultRef}>
            <h3>
              7-Day Irrigation Plan — {formData.district} / {formData.crop} / {formData.growth_stage}
            </h3>

            <div className="table-wrap">
              <table className="result-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Soil Moisture (%)</th>
                    <th>Stage Threshold (%)</th>
                    <th>Rain (mm)</th>
                    <th>ET₀ (mm)</th>
                    <th>Deficit</th>
                    <th>Water (L/ha)</th>
                    <th>Irrigation</th>
                  </tr>
                </thead>
                <tbody>
                  {result.map((r, i) => (
                    <tr key={i} style={{ background: r.needs_irrigation ? "#fff0f0" : "#f3fff5" }}>
                      <td>{r.date}</td>
                      <td>{r.predicted_soil_moisture_percent.toFixed(2)}</td>
                      <td>{r.growth_stage_threshold}</td>
                      <td>{r.rain_mm}</td>
                      <td>{r.et0_mm}</td>
                      <td>{r.moisture_deficit_mm}</td>
                      <td>{r.water_l_per_hectare}</td>
                      <td>{r.needs_irrigation ? "Yes" : "No"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* CHART */}
            <div className="chart-wrap">
              <Line data={chartData} options={chartOptions} />
            </div>
          </section>
        )}

      </div>
    </div>
  );
}
