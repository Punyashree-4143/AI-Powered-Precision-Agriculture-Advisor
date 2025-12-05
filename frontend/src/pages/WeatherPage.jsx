import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import WeatherForecast from "../components/WeatherForecast";
import "../styles/WeatherPage.css";
  // ✅ IMPORTANT for sidebar spacing

export default function WeatherPage() {
  const [data, setData] = useState(null);
  const [location, setLocation] = useState("Bangalore");

  const navigate = useNavigate();

  const fetchWeather = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/weather", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location })
      });

      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Weather fetch failed:", err);
    }
  };

  useEffect(() => {
    fetchWeather();
  }, []);

  return (
    <div className="page-content">      {/* ✅ FIXED: no overlap with sidebar */}
      <div className="weather-page">

        

        {/* HEADER */}
        <h1 className="wp-title">🌤 Weather Forecast</h1>

        {/* SEARCH AREA */}
        <div className="wp-search-box">
          <input
            type="text"
            placeholder="Search a location... (e.g., Bangalore)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="wp-input"
          />

          <button onClick={fetchWeather} className="wp-btn">
            Search
          </button>
        </div>

        {/* Weather Output */}
        <div className="wp-forecast-container">
          <WeatherForecast data={data} />
        </div>
      </div>
    </div>
  );
}
