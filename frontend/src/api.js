import axios from "axios";

// ===============================
// ENV VARIABLES (Vite)
// ===============================
const API_BASE = import.meta.env.VITE_API_BASE;
const CROP_API_BASE = import.meta.env.VITE_CROP_API;

// ===============================
// MAIN BACKEND
// ===============================
export const API = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 20000,
});

API.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("MAIN API ERROR:", err?.response || err);
    throw err;
  }
);

// ===============================
// CROP RECOMMENDATION BACKEND
// ===============================
export const CropAPI = axios.create({
  baseURL: CROP_API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 20000,
});

CropAPI.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("CROP API ERROR:", err?.response || err);
    throw err;
  }
);

// ===============================
// FUNCTIONS / ENDPOINTS
// ===============================

// Dropdown data
export const fetchStates = () => API.get("/get-states");
export const fetchDistricts = (state) =>
  API.get(`/get-districts?state=${state}`);
export const fetchMarkets = (district) =>
  API.get(`/get-markets?district=${district}`);
export const fetchCommodities = () => API.get("/get-commodities");

// Crop recommendation (CROP BACKEND)
export const getCropRecommendation = (data) =>
  CropAPI.post("/crop-recommend", data);

// Yield prediction (MAIN BACKEND)
export const getYieldPrediction = (data) =>
  API.post("/yield-predict", data);

// Irrigation
export const getIrrigation = (data) =>
  API.post("/irrigation", data);

// Weather
export const getWeather = (location) =>
  API.post("/weather", { location });
