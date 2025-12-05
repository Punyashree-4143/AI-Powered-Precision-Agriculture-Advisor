// src/components/IrrigationResultCard.jsx

const IrrigationResultCard = ({ data }) => {
  return (
    <div className="bg-white shadow-md p-4 rounded-xl space-y-2">
      <h3 className="text-lg font-semibold text-gray-700">
        📅 {data.date}
      </h3>

      <p>
        <strong>Predicted Soil Moisture:</strong> {data.predicted_soil_moisture_percent}%
      </p>

      <p>
        <strong>Rainfall:</strong> {data.rain_mm} mm
      </p>

      <p>
        <strong>ET₀:</strong> {data.et0_mm} mm
      </p>

      <p>
        <strong>Moisture Deficit:</strong> {data.moisture_deficit_mm} mm
      </p>

      {data.needs_irrigation ? (
        <p className="text-red-600 font-semibold">
          🚨 Needs Irrigation  
          <br />
          💧 Water Required: {data.water_l_per_hectare} L/ha
        </p>
      ) : (
        <p className="text-green-600 font-semibold">✔ No Irrigation Needed</p>
      )}
    </div>
  );
};

export default IrrigationResultCard;
