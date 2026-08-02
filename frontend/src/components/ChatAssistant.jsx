import { useState } from "react";

export default function ChatAssistant() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/vehicles/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      setAnswer(await res.json());
    } catch (err) {
      setError(err.message);
      setAnswer(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && ask()}
        placeholder="e.g. cars under 26k, sedan, similar to an Accord"
        style={{ width: "100%", padding: 8 }}
      />
      <button onClick={ask} disabled={loading} style={{ marginTop: 8 }}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {answer && (
        <div style={{ marginTop: 16 }}>
          <p>Found {answer.count} matches.</p>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>Model</th>
                <th style={{ textAlign: "left" }}>Price</th>
                <th style={{ textAlign: "left" }}>Body Type</th>
              </tr>
            </thead>
            <tbody>
              {answer.results.map((r, i) => (
                <tr key={i}>
                  <td>{r.model}</td>
                  <td>${r.price}</td>
                  <td>{r.body_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}