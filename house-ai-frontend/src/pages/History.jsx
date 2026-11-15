import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getHistory } from "../api";

export default function History() {
  const [items, setItems] = useState(null); // null = still loading
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    getHistory()
      .then(setItems)
      .catch(() => setErrorMsg("Couldn't load your history."));
  }, []);

  return (
    <section className="history">
      <Link to="/" className="back-link">← Ask something new</Link>
      <h1 className="history-page-title">Your history</h1>

      {errorMsg && <p className="fallback-note">{errorMsg}</p>}
      {!items && !errorMsg && <p className="fallback-note">Loading…</p>}
      {items && items.length === 0 && (
        <p className="fallback-note">Nothing here yet — go ask your first question!</p>
      )}

      <ul className="history-list">
        {items?.map((item) => (
          <li key={item.id}>
            {/* Clicking a row opens the full question + answer */}
            <Link to={`/history/${item.id}`} className="history-row">
              <span className="history-query">{item.query}</span>
              <p className="history-answer">{item.preview}</p>
              <span className="history-date">
                {new Date(item.created_at).toLocaleString()}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
