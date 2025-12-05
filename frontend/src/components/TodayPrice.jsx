import { useState } from "react";
import { getTodayPrice, listModels } from "../api";

export default function TodayPrice() {
  const [models, setModels] = useState([]);
  const [commodity, setCommodity] = useState("");
  const [market, setMarket] = useState("");
  const [result, setResult] = useState(null);

  // Load model list at start
  useState(() => {
    listModels().then((res) => setModels(res.data.files));
  }, []);

  const commodities = [...new Set(models.map((f) => f.split("__")[0]))];
  const markets = commodity
    ? [...new Set(models.filter((f) => f.startsWith(commodity)).map((f) => f.split("__")[1]))]
    : [];

  const fetchPrice = () => {
    if (!commodity || !market) return;
    getTodayPrice(commodity, market).then((res) => setResult(res.data));
  };

  return (
    <div>
      <h2>Today Price Prediction</h2>

      <select value={commodity} onChange={(e) => setCommodity(e.target.value)}>
        <option value="">Select Commodity</option>
        {commodities.map((c, i) => (
          <option key={i}>{c}</option>
        ))}
      </select>

      <select value={market} onChange={(e) => setMarket(e.target.value)}>
        <option value="">Select Market</option>
        {markets.map((m, i) => (
          <option key={i}>{m}</option>
        ))}
      </select>

      <button onClick={fetchPrice}>Predict Today Price</button>

      {result && (
        <div style={{ marginTop: "10px" }}>
          <h4>₹ {result.predicted_price}</h4>
        </div>
      )}
    </div>
  );
}
