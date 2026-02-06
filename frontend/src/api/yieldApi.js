// src/api/yield.js
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE;

if (!API_BASE) {
  console.error("❌ REACT_APP_API_BASE is missing. Check .env or Vercel env vars.");
}

const API_URL = `${API_BASE}/yield-predict`;

export const predictYield = async (payload) => {
  try {
    const res = await axios.post(API_URL, payload, {
      headers: { "Content-Type": "application/json" },
      timeout: 20000,
    });
    return res.data;
  } catch (error) {
    console.error("Yield prediction error:", error);
    return error.response?.data || { error: "Server error" };
  }
};
