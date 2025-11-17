import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

export default function ActualVsPredictedChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch y_test and y_pred from FastAPI
    fetch("http://localhost:8000/metrics/actual-vs-predicted")
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  if (!data) return <div>Loading...</div>;

  const { y_test, y_pred } = data;

  // For diagonal line
  const minVal = Math.min(...y_test);
  const maxVal = Math.max(...y_test);

  return (
  <div
    style={{
      width: "100%",
      minHeight: "600px",
      overflow: "visible",
      paddingBottom: "40px",
    }}
  >
    <Plot
      data={[
        {
          x: y_test,
          y: y_pred,
          mode: "markers",
          type: "scatter",
          name: "Predictions",
          marker: { color: "blue" },
        },
        {
          x: [minVal, maxVal],
          y: [minVal, maxVal],
          mode: "lines",
          name: "Perfect Prediction",
          line: { dash: "dash", color: "red" },
        },
      ]}
      layout={{
        title: {
          text: "Actual vs Predicted Prices",
          font: { size: 22 },
        },
        xaxis: {
          title: {
            text: "Actual Price",
            standoff: 20,
          },
        },
        yaxis: {
          title: {
            text: "Predicted Price",
            standoff: 20,
          },
        },
        autosize: true,
        height: 550,
        margin: { l: 80, r: 40, t: 80, b: 80 },
      }}
      style={{
        width: "100%",
        overflow: "visible",
      }}
      useResizeHandler={true}
      config={{ responsive: true }}
    />
  </div>
);
}
