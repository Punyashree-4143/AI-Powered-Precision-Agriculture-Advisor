import axios from "axios";

// MAIN BACKEND (Port 5000)
export const API = axios.create({
  baseURL: "http://localhost:5000/api",   // <-- adjust if backend runs elsewhere
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

API.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("MAIN API ERROR:", err);
    throw err;
  }
);

// PROPHET BACKEND (Port 5001)
export const ProphetAPI = axios.create({
  baseURL: "http://localhost:5001/api",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

ProphetAPI.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("PROPHET API ERROR:", err);
    throw err;
  }
);

// ------------------------
// FUNCTIONS / ENDPOINTS
// ------------------------

// Models
export const listModels = () => API.get("/models/list");

// Market prices
export const getTodayPrice = (commodity, market) =>
  API.get(`/predict/today?commodity=${commodity}&market=${market}`);

export const getForecast7 = (commodity, market) =>
  ProphetAPI.get(`/forecast/7?commodity=${commodity}&market=${market}`);

// Dropdown data
export const fetchStates = () => API.get("/get-states");
export const fetchDistricts = (state) => API.get(`/get-districts?state=${state}`);
export const fetchMarkets = (district) => API.get(`/get-markets?district=${district}`);
export const fetchCommodities = () => API.get("/get-commodities");

// Crop and yield
export const getCropRecommendation = (data) => API.post("/crop-recommend", data);
export const getYieldPrediction = (data) => API.post("/yield-predict", data);

// NEW: Irrigation Planner
export const getIrrigation = (data) => API.post("/irrigation", data);

// NEW: Weather API (optional)
export const getWeather = (location) => API.post("/weather", { location });
