import React from "react";

const YieldResult = ({ result }) => {
  if (!result) return null;

  if (result.error) {
    return <div className="alert alert-danger">❌ {result.error}</div>;
  }

  return (
    <div className="mt-4 p-3 border rounded">
      <h3>📊 Prediction Result</h3>

      <p><b>District:</b> {result.District}</p>
      <p><b>Crop:</b> {result.Crop}</p>
      <p><b>Area (acres):</b> {result.area_acre}</p>

      <p><b>Yield per hectare:</b> {result.yield_ton_per_hectare} tons</p>
      <p><b>Yield per acre:</b> {result.yield_ton_per_acre} tons</p>
      <p><b>Total Expected Yield:</b> {result.total_yield_tonnes} tons</p>
    </div>
  );
};

export default YieldResult;
