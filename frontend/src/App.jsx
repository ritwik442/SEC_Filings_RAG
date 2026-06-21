import { useState, useEffect } from "react";


const API_BASE = "http://localhost:8000";

export default function App() {

  const [question, setQuestion] = useState("");
  const [company, setCompany] = useState("");
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);


  useEffect(() => {
    fetch(`${API_BASE}/companies`)
      .then((r) => r.json())
      .then((data) => setCompanies(data.companies))
      .catch((e) => console.error("Failed to load companies:", e));
  }, []);

  async function handleAsk() {
    if (!question.trim()) return;        
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          k: 6,
          company: company || null,
        }),
      });

      if (!resp.ok) {

        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || `HTTP ${resp.status}`);
      }

      setResult(await resp.json());
    } catch (e) {
      setError(e.message);
    } finally {

      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="max-w-3xl mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold mb-2">SEC Filings Q&A</h1>
          <p className="text-slate-600">
            Ask grounded questions about real SEC filings. Every answer is
            sourced from the original document.
          </p>
        </header>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <label className="block text-sm font-medium mb-1">Company</label>
          <select
            className="w-full mb-4 p-2 border border-slate-300 rounded"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          >
            <option value="">All companies</option>
            {companies.map((c) => (
              <option key={c.ticker} value={c.ticker}>
                {c.ticker.toUpperCase()} ({c.filings.join(", ")})
              </option>
            ))}
          </select>

          <label className="block text-sm font-medium mb-1">Question</label>
          <textarea
            className="w-full p-2 border border-slate-300 rounded mb-4"
            rows={3}
            placeholder="e.g. What was the IPO offer price per share?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === "Enter") handleAsk();
            }}
          />

          <button
            onClick={handleAsk}
            disabled={loading || !question.trim()}
            className="bg-slate-900 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded mb-6">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="font-semibold mb-2">Answer</h2>
              {/* whitespace-pre-wrap preserves the model's line breaks so
                  bullet-pointed answers stay readable. */}
              <p className="whitespace-pre-wrap">{result.answer}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="font-semibold mb-3">
                Sources ({result.sources.length})
              </h2>
              <div className="space-y-3">
                {result.sources.map((s, i) => (

                  <div key={i} className="border-l-2 border-slate-300 pl-3 text-sm">
                    <div className="text-slate-500 mb-1">
                      {s.company.toUpperCase()} {s.filing_type} · chunk {s.chunk_index} · score {s.score}
                    </div>
                    <div className="text-slate-700">{s.preview}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}