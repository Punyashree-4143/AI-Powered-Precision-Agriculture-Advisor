// src/api/irrigation.js

export async function getIrrigationPlan(payload) {
  const res = await fetch(
    "https://ai-powered-precision-agriculture-advisor.onrender.com/api/irrigation",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch irrigation data");
  }

  return await res.json();
}
