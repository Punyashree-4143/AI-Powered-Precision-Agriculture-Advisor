import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/WeatherForecast.css";

export default function WeatherForecast({ data }) {
  const navigate = useNavigate();

  if (!data || !data.today_weather || !data.forecast_7_days) {
    return <div className="weather-container">Loading weather...</div>;
  }

  const today = data.today_weather;
  const weekly = data.forecast_7_days;

  const getIcon = (code, rainChance = 0) => {
    const iconMap = {
      0: "☀️", 1: "🌤️", 2: "⛅", 3: "🌥️",
      45: "🌫️", 48: "🌁",
      51: "🌦️", 53: "🌦️", 55: "🌧️",
      61: "🌧️", 63: "🌧️", 65: "🌧️",
      80: "🌦️", 81: "🌧️", 82: "🌧️",
      95: "⛈️", 96: "⛈️", 99: "⛈️"
    };

    if (rainChance < 30 && (code === 95 || code === 96 || code === 99)) {
      return "🌦️";
    }
    return iconMap[code] || "🌤️";
  };

  const formatDate = (d) => {
    const x = new Date(d);
    return x.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  return (
    <div className="weather-container">

      

      {/* 🔥 TODAY WEATHER – Highlighted */}
      <div className="today-highlight">
        <div className="today-header">
          Today – {formatDate(today.date)}
        </div>

        <div className="today-main">
          <div className="today-left">
            <div className="today-icon">{getIcon(today.weather_code)}</div>
            <div className="today-temp">{today.max_temp_c}°C</div>
            <div className="today-feels">
              Feels like {today.max_temp_c + 1}°C
            </div>
          </div>

          <div className="today-details">
            <p>🌡 Max: {today.max_temp_c}°C</p>
            <p>🌡 Min: {today.min_temp_c}°C</p>
            <p>💧 Humidity: {today.humidity}%</p>
            <p>🌧 Rain: {today.rain_chance}% ({today.rain_mm} mm)</p>
            <p>💨 Wind: {today.wind_speed} km/h</p>
            <p>🧭 Direction: {today.wind_direction}</p>
            <p>☁️ Clouds: {today.cloud_cover}%</p>
            <p>💧 Dew Point: {today.dew_point}°C</p>
            <p>🔆 UV Index: {today.uv_index}</p>
          </div>
        </div>
      </div>

      {/* WEEKLY FORECAST */}
      <div className="weekly-title">7-Day Forecast</div>

      <div className="weekly-grid">
        {weekly.map((day, idx) => (
          <div key={idx} className="week-card">

            <div className="week-top">
              <span className="week-date">{formatDate(day.date)}</span>
              <span className="week-icon">{getIcon(day.weather_code, day.rain_chance)}</span>
            </div>

            <div className="week-line">
              🌡 Max: {day.max_temp_c}° • Min: {day.min_temp_c}°
            </div>

            <div className="week-line">
              🌧 Rain: {day.rain_chance}% ({day.rain_mm} mm)
            </div>

            <div className="week-line">
              💧 Humidity: {day.humidity}%
            </div>

            <div className="week-line">
              💨 Wind: {day.wind_speed} km/h
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
