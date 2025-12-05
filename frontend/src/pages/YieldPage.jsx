import React, { useState } from "react";
import YieldForm from "../components/YieldForm";
import YieldResult from "../components/YieldResult";
import "../styles/yield.css";

const YieldPage = () => {
  const [result, setResult] = useState(null);

  return (
    <div className="yield-container">
      <YieldForm onResult={setResult} />
      <YieldResult result={result} />
    </div>
  );
};

export default YieldPage;
