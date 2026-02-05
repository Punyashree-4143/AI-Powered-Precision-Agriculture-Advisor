import React from "react";

const YieldResult = ({ result }) => {
  if (!result) return null;

  if (result.status !== "success") {
    return (
      <div className="yield-result error">
        ❌ {result.message || "Yield prediction failed"}
      </div>
    );
  }

  return (
    <div className="yield-result">
      <h3>📊 Prediction Result</h3>

      <div className="result-horizontal">
        <div>
          <span>District</span>
          <p>{result.District}</p>
        </div>

        <div>
          <span>Crop</span>
          <p>{result.Crop}</p>
        </div>

        <div>
          <span>Area (acres)</span>
          <p>{result.area_acre}</p>
        </div>

        <div>
          <span>Yield / ha</span>
          <p>{result.yield_ton_per_hectare} t</p>
        </div>

        <div>
          <span>Yield / acre</span>
          <p>{result.yield_ton_per_acre} t</p>
        </div>

        <div>
          <span>Total Yield</span>
          <p>{result.total_yield_tonnes} t</p>
        </div>
      </div>
    </div>
  );
};

export default YieldResult;
