import React, { useState, useRef } from "react";
import "./App.css";

/**
 * ----------------------------------------------------------------------
 * BACKEND CALL
 * ----------------------------------------------------------------------
 * Calls your FastAPI backend's /chat route. Your graph handles query
 * classification (food / appliance / energy) and recommendation
 * generation internally — this just sends the raw query and shows
 * whatever text comes back.
 *
 * Requires VITE_API_URL to be set (in a local .env file, and as an
 * Environment Variable in your frontend's Vercel project settings) to
 * your backend's deployed URL, e.g. https://your-backend.vercel.app
 * ----------------------------------------------------------------------
 */
async function askAssistant(message) {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) throw new Error("Request failed");
  const data = await res.json();
  return data.response;
}

/**
 * ----------------------------------------------------------------------
 * UI COMPONENTS
 * ----------------------------------------------------------------------
 */
function HistoryRow({ entry }) {
  return (
    <li className="history-row">
      <span className="history-query">{entry.query}</span>
      <p className="history-answer">{entry.answer}</p>
    </li>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const inputRef = useRef(null);

  const handleSubmit = async () => {
    const trimmed = query.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setErrorMsg(null);

    try {
      const reply = await askAssistant(trimmed);
      setAnswer(reply);
      setHistory((prev) =>
        [{ query: trimmed, answer: reply, id: Date.now() }, ...prev].slice(0, 8)
      );
      setQuery("");
    } catch (err) {
      setErrorMsg("Couldn't reach the assistant — try again in a moment.");
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="app">
      <div className="glow glow--top" />
      <div className="glow glow--bottom" />

      <header className="hero">
        <span className="eyebrow">Household AI Assistant</span>
        <h1 className="hero-title">
          Ask your home
          <br />
          anything.
        </h1>
        <p className="hero-subtitle">
          Food safety, appliances, or energy saving — ask in plain
          language and get a recommendation back.
        </p>
      </header>

      <section className="switchboard">
        <div className="query-bar">
          <input
            ref={inputRef}
            className="query-input"
            type="text"
            placeholder="e.g. My fridge is making a loud humming noise"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="query-submit"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Thinking…" : "Ask"}
          </button>
        </div>

        {errorMsg && <p className="fallback-note">{errorMsg}</p>}

        {answer && !errorMsg && (
          <div className="answer-card">
            <span className="answer-label">Recommendation</span>
            <p className="answer-text">{answer}</p>
          </div>
        )}
      </section>

      {history.length > 0 && (
        <section className="history">
          <h2 className="history-title">Recent queries</h2>
          <ul className="history-list">
            {history.map((entry) => (
              <HistoryRow key={entry.id} entry={entry} />
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}