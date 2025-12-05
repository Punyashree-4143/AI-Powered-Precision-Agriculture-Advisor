import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/Navbar.css";

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav
      className="navbar"
      style={{
        left: token ? "230px" : "0px",
        width: token ? "calc(100% - 230px)" : "100%",
      }}
    >
      {/* LEFT SIDE */}
      <div className="nav-left">
        <span className="nav-logo">🌾</span>
        <span className="nav-title">Smart Agriculture Advisor</span>
      </div>

      
    </nav>
  );
}
