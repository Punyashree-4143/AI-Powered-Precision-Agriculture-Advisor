import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "../styles/Sidebar.css";

export default function Sidebar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  if (!token) return null; // hide sidebar if logged out

  return (
    <div className="sidebar">
      <h3 className="sidebar-title">🌾 Agri Advisor</h3>

      <NavLink to="/home" className="side-item">🏠 Home</NavLink>
      <NavLink to="/crop-recommendation" className="side-item">🌱 Crop Recommendation</NavLink>
      <NavLink to="/disease-prediction" className="side-item">🦠 Disease Predictor</NavLink>
      <NavLink to="/yield-prediction" className="side-item">📊 Yield Prediction</NavLink>
      <NavLink to="/weather-forecast" className="side-item">🌦 Weather Forecast</NavLink>
      <NavLink to="/irrigation-planner" className="side-item">💧 Irrigation Planner</NavLink>
      <NavLink to="/market-forecast" className="side-item">📈 Market Forecast</NavLink>
      <NavLink to="/profile" className="side-item">👤 Profile</NavLink>

      <button
        className="logout-btn"
        onClick={() => {
          localStorage.removeItem("token");
          navigate("/login");
        }}
      >
        Logout
      </button>
    </div>
  );
}
