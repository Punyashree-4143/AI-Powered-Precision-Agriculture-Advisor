import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Dashboard.css";

/* 🔧 CHANGE THIS TO YOUR DEPLOYED BACKEND URL */
const BACKEND_URL = "https://ai-powered-precision-agriculture-advisor.onrender.com/";

const Dashboard = () => {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // token handling
  const [token, setToken] = useState(null);

  useEffect(() => {
    const t = localStorage.getItem("token");
    setToken(t);
  }, []);

  // Fetch profile once token is ready
  useEffect(() => {
    if (!token) return;

    fetch(`${BACKEND_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch profile");
        return res.json();
      })
      .then((data) => setProfile(data))
      .catch((err) => {
        console.error("Profile fetch error:", err);
        localStorage.removeItem("token");
        navigate("/login");
      });
  }, [token, navigate]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (token === null) return null;

  // Not logged in
  if (!token) {
    return (
      <div className="dashboard-wrapper auth-screen">
        <header className="dashboard-header">
          <h1>🌾 Smart Agriculture Advisor</h1>
          <p>Please login or register to access the modules</p>
        </header>

        <div className="auth-buttons">
          <button
            className="register-btn"
            onClick={() => navigate("/register")}
          >
            Register
          </button>
          <button
            className="login-btn"
            onClick={() => navigate("/login")}
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-wrapper">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-left">
          <span style={{ fontSize: "26px" }}>🌿</span>
          <h2>Smart Agriculture Advisor</h2>
        </div>

        <div className="navbar-center">
          AI-powered decision support system
        </div>

        <div className="navbar-right" ref={dropdownRef}>
          <div
            className="user-icon"
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            👤 {profile?.name} ▼
          </div>

          {dropdownOpen && (
            <div className="profile-menu">
              <div onClick={() => navigate("/profile")}>My Profile</div>
              <div
                onClick={() => {
                  localStorage.removeItem("token");
                  navigate("/login");
                }}
              >
                Logout
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Header */}
      <header className="dashboard-header">
        <h1>Welcome, {profile?.name} 👋</h1>
        <p>Choose a module to get started</p>
      </header>

      {/* Modules */}
      <div className="dashboard-grid">
        <div
          className="dashboard-card"
          onClick={() => navigate("/crop-recommendation")}
        >
          <div className="card-icon">🌱</div>
          <h2>Crop Recommendation</h2>
          <p>Suggests best crops based on soil & climate</p>
        </div>

        <div
          className="dashboard-card"
          onClick={() => navigate("/yield-prediction")}
        >
          <div className="card-icon">📊</div>
          <h2>Yield Prediction</h2>
          <p>Predict future yield using ML ensemble models</p>
        </div>

        <div
          className="dashboard-card"
          onClick={() => navigate("/weather-forecast")}
        >
          <div className="card-icon">⛅</div>
          <h2>Weather Forecast</h2>
          <p>Next 7 days climate & rainfall insights</p>
        </div>

        <div
          className="dashboard-card"
          onClick={() => navigate("/market-forecast")}
        >
          <div className="card-icon">📈</div>
          <h2>Market Price Analysis</h2>
          <p>Predict commodity prices across markets</p>
        </div>

        <div
          className="dashboard-card"
          onClick={() => navigate("/irrigation-planner")}
        >
          <div className="card-icon">💧</div>
          <h2>Irrigation Planner</h2>
          <p>Optimize irrigation based on soil & rainfall</p>
        </div>

        <div
          className="dashboard-card"
          onClick={() => navigate("/disease-detection")}
        >
          <div className="card-icon">🦠</div>
          <h2>Plant Disease Detection</h2>
          <p>Detect plant diseases using your leaf images</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
