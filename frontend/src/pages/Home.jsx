import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Home.css";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="premium-home-container">

      {/* HERO SECTION */}
      <section className="hero-section">
        <div className="overlay"></div>

        <div className="hero-content" data-aos="fade-up">
          <h1 className="hero-title">
            🌾 Empowering Agriculture with <span>Artificial Intelligence</span>
          </h1>

          <p className="hero-subtitle">
            Make smarter farming decisions with AI-driven crop prediction,
            irrigation planning, weather forecasting, market forecasting,
            disease detection, and yield estimation.
          </p>

          <div className="hero-buttons">
            <button
              className="btn-premium login-btn"
              onClick={() => navigate("/login")}
            >
              Login
            </button>

            <button
              className="btn-premium register-btn"
              onClick={() => navigate("/register")}
            >
              Register
            </button>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="features-section">
        <h2 className="features-title">Powerful Farming Intelligence</h2>

        <div className="features-grid">

          {/* 1 — Crop Recommendation */}
          <div className="feature-card" data-aos="zoom-in">
            <div className="icon-circle">🌱</div>
            <h3>Crop Recommendation</h3>
            <p>
              Get AI-based suggestions for ideal crops using soil nutrients,
              weather conditions, and environmental data.
            </p>
          </div>

          {/* 2 — Disease Predictor */}
          <div className="feature-card" data-aos="zoom-in" data-aos-delay="150">
            <div className="icon-circle">🦠</div>
            <h3>Disease Predictor</h3>
            <p>
              Detect crop diseases early using deep learning image analysis
              and smart diagnosis.
            </p>
          </div>

          {/* 3 — Yield Prediction */}
          <div className="feature-card" data-aos="zoom-in" data-aos-delay="300">
            <div className="icon-circle">📊</div>
            <h3>Yield Prediction</h3>
            <p>
              Predict crop yields using machine learning algorithms to plan
              harvest and resources efficiently.
            </p>
          </div>

          {/* 4 — Weather Forecast */}
          <div className="feature-card" data-aos="zoom-in" data-aos-delay="450">
            <div className="icon-circle">🌦️</div>
            <h3>Weather Forecast</h3>
            <p>
              Access 7-day weather forecasts to optimize irrigation and
              crop growth cycles.
            </p>
          </div>

          {/* 5 — Irrigation Planner */}
          <div className="feature-card" data-aos="zoom-in" data-aos-delay="600">
            <div className="icon-circle">💧</div>
            <h3>Irrigation Planner</h3>
            <p>
              Get optimized irrigation schedules using ET₀, soil moisture,
              rainfall, and crop water needs.
            </p>
          </div>

          {/* 6 — Market Forecast */}
          <div className="feature-card" data-aos="zoom-in" data-aos-delay="750">
            <div className="icon-circle">📈</div>
            <h3>Market Forecast</h3>
            <p>
              Analyze future crop prices using predictive analytics to sell
              at the best time and maximize profits.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
}
