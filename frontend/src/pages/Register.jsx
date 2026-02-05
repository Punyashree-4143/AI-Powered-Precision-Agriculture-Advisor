import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

/* 🔧 BACKEND URL
   Replace with your actual Render backend URL */
const REGISTER_API =
  "https://ai-powered-precision-agriculture-advisor.onrender.com/api/auth/register";


export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    state: "",
    district: "",
    farmSize: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(REGISTER_API, form, {
        headers: { "Content-Type": "application/json" },
      });
      alert("Registration successful!");
      navigate("/login");
    } catch (err) {
      alert(err.response?.data?.msg || "Registration failed");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Create Account</h2>

        <form onSubmit={handleSubmit} style={styles.form}>

          <input
            type="text"
            placeholder="Full Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            style={styles.input}
            required
          />

          <input
            type="email"
            placeholder="Email Address"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            style={styles.input}
            required
          />

          <input
            type="tel"
            placeholder="Phone Number"
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
            style={styles.input}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            style={styles.input}
            required
          />

          <input
            type="text"
            placeholder="State"
            value={form.state}
            onChange={(e) => setForm({ ...form, state: e.target.value })}
            style={styles.input}
            required
          />

          <input
            type="text"
            placeholder="District"
            value={form.district}
            onChange={(e) => setForm({ ...form, district: e.target.value })}
            style={styles.input}
            required
          />

          <input
            type="number"
            placeholder="Farm Size (in acres)"
            value={form.farmSize}
            onChange={(e) => setForm({ ...form, farmSize: e.target.value })}
            style={styles.input}
            required
          />

          <button type="submit" style={styles.button}>
            Register
          </button>

          <p style={styles.text}>
            Already have an account?{" "}
            <span
              style={styles.link}
              onClick={() => navigate("/login")}
            >
              Login
            </span>
          </p>

        </form>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#eef5ee",
  },
  card: {
    width: "380px",
    padding: "30px",
    borderRadius: "12px",
    background: "#fff",
    boxShadow: "0px 4px 15px rgba(0,0,0,0.1)",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
    color: "#2c6e49",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
  },
  input: {
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    outline: "none",
  },
  button: {
    padding: "12px",
    border: "none",
    borderRadius: "8px",
    background: "#2c6e49",
    color: "#fff",
    cursor: "pointer",
    fontSize: "16px",
  },
  text: {
    marginTop: "10px",
    textAlign: "center",
  },
  link: {
    color: "#2c6e49",
    cursor: "pointer",
    fontWeight: "bold",
  },
};
