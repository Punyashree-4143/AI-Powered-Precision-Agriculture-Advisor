// src/api/irrigation.js

export async function getIrrigationPlan(payload) {
  const res = await fetch("http://localhost:5000/api/irrigation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch irrigation data");
  }

  return await res.json();
}
