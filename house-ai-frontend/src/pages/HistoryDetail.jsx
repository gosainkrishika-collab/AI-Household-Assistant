import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { getHistoryItem } from "../api";

export default function HistoryDetail() {
  const { id } = useParams(); // the number in /history/:id
  const [item, setItem] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    getHistoryItem(id)
      .then(setItem)
      .catch(() => setErrorMsg("Couldn't find that query."));
  }, [id]);

  return (
    <section className="history">
      <Link to="/history" className="back-link">← Back to history</Link>

      {errorMsg && <p className="fallback-note">{errorMsg}</p>}
      {!item && !errorMsg && <p className="fallback-note">Loading…</p>}

      {item && (
        <div className="answer-card">
          <p className="answer-question">“{item.query}”</p>
          <span className="answer-label">Recommendation</span>
          <p className="answer-text">{item.answer}</p>
          <span className="history-date">
            {new Date(item.created_at).toLocaleString()}
          </span>
        </div>
      )}
    </section>
  );
}
