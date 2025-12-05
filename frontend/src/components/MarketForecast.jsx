import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import "../styles/MarketPrice.css";


export default function MarketForecast() {
  const navigate = useNavigate();

  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [commodities, setCommodities] = useState([]);

  const [selectedState, setSelectedState] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedMarket, setSelectedMarket] = useState("");
  const [selectedCommodity, setSelectedCommodity] = useState("");

  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const BASE = "http://127.0.0.1:5000";

  // Load states + commodities
  useEffect(() => {
    axios.get(`${BASE}/api/get-states`)
      .then(res => setStates(res.data.states || []))
      .catch(() => setStates([]));

    axios.get(`${BASE}/api/get-commodities`)
      .then(res => setCommodities(res.data.commodities || []))
      .catch(() => setCommodities([]));
  }, []);

  const handleStateChange = (state) => {
    setSelectedState(state);
    setSelectedDistrict("");
    setSelectedMarket("");
    setDistricts([]);
    setMarkets([]);

    if (!state) return;

    axios.get(`${BASE}/api/get-districts?state=${encodeURIComponent(state)}`)
      .then(res => setDistricts(res.data.districts?.Karnataka || []))
      .catch(() => setDistricts([]));
  };

  const handleDistrictChange = (district) => {
    setSelectedDistrict(district);
    setSelectedMarket("");
    setMarkets([]);

    if (!district) return;

    axios.get(`${BASE}/api/get-markets?district=${encodeURIComponent(district)}`)
      .then(res => setMarkets(res.data.markets || []))
      .catch(() => setMarkets([]));
  };

  const getForecast = async () => {
    setError("");

    if (!selectedDistrict || !selectedMarket || !selectedCommodity) {
      setError("Please select District, Market and Commodity.");
      return;
    }

    setLoading(true);
    setForecast([]);

    try {
      const payload = {
        district: selectedDistrict,
        market: selectedMarket,
        commodity: selectedCommodity
      };

      const res = await axios.post(`${BASE}/api/market/predict7`, payload);
      if (res.data.predictions) {
        setForecast(res.data.predictions);
      } else {
        setError(res.data.error || "Unexpected response");
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }

    setLoading(false);
  };

  const chartData = forecast.map(p => ({
    date: p.date,
    price: Number(p.predicted_price)
  }));

  return (
    <div className="page-content">   {/* ✅ FIXED: No sidebar overlap */}
      <div className="market-container">


        <h2>📈 7-Day Market Price Forecast</h2>

        <div className="form-box">

          <div className="select-row">
            <select
              value={selectedState}
              onChange={e => handleStateChange(e.target.value)}
            >
              <option value="">Select State</option>
              {states.map((s, i) => <option key={i} value={s}>{s}</option>)}
            </select>

            <select
              value={selectedDistrict}
              onChange={e => handleDistrictChange(e.target.value)}
            >
              <option value="">Select District</option>
              {districts.map((d, i) => <option key={i} value={d}>{d}</option>)}
            </select>

            <select
              value={selectedMarket}
              onChange={e => setSelectedMarket(e.target.value)}
            >
              <option value="">Select Market</option>
              {markets.map((m, i) => <option key={i} value={m}>{m}</option>)}
            </select>

            <select
              value={selectedCommodity}
              onChange={e => setSelectedCommodity(e.target.value)}
            >
              <option value="">Select Commodity</option>
              {commodities.map((c, i) => <option key={i} value={c}>{c}</option>)}
            </select>
          </div>

          <button onClick={getForecast} disabled={loading}>
            {loading ? "Loading..." : "Get Forecast"}
          </button>

        </div>

        {error && <div className="error">{error}</div>}

        {forecast.length > 0 && (
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#007bff" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
