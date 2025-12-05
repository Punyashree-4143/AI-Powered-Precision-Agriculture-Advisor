import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard"; 

import Home from "./pages/Home";
import Profile from "./pages/Profile";
import Login from "./pages/Login";
import Register from "./pages/Register";

import CropRecommendation from "./components/CropRecommendation";
import MarketForecast from "./components/MarketForecast";
import IrrigationPlanner from "./components/IrrigationPlanner";
import WeatherPage from "./pages/WeatherPage";
import YieldPage from "./pages/YieldPage";
import DiseasePredictor from "./components/DiseasePredictor";

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
};

function LayoutWrapper({ children }) {
  const token = localStorage.getItem("token");
  const location = useLocation();

  const noLayoutRoutes = ["/login", "/register"];
  const isAuthPage = noLayoutRoutes.includes(location.pathname);

  const showLayout = token && !isAuthPage;

  return (
    <>
      {showLayout && <Navbar />}
      {showLayout && <Sidebar />}

      <div
        style={{
          marginLeft: showLayout ? "230px" : "0",
          marginTop: showLayout ? "70px" : "0",
          padding: "20px",
        }}
      >
        {children}
      </div>
    </>
  );
}

export default function App() {
  return (
    <Router>
      <LayoutWrapper>
        <Routes>
          <Route path="/" element={<Navigate to="/home" />} />

          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/crop-recommendation" element={<ProtectedRoute><CropRecommendation /></ProtectedRoute>} />
          <Route path="/weather-forecast" element={<ProtectedRoute><WeatherPage /></ProtectedRoute>} />
          <Route path="/market-forecast" element={<ProtectedRoute><MarketForecast /></ProtectedRoute>} />
          <Route path="/yield-prediction" element={<ProtectedRoute><YieldPage /></ProtectedRoute>} />
          <Route path="/disease-prediction" element={<ProtectedRoute><DiseasePredictor /></ProtectedRoute>} />
          <Route path="/irrigation-planner" element={<ProtectedRoute><IrrigationPlanner /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}
