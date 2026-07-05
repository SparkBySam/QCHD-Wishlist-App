import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import SearchBar from "../components/SearchBar";

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export default function Matches() {
  const [matches, setMatches] = useState([]);
  const [search, setSearch] = useState("");
  const [unhandledOnly, setUnhandledOnly] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadMatches = useCallback(async () => {
    setError("");
    try {
      const data = await api.getMatches(search, unhandledOnly);
      setMatches(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search, unhandledOnly]);

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  async function toggleNotified(match, event) {
    event.stopPropagation();
    try {
      const updated = await api.setMatchNotified(match.id, !match.notified);
      setMatches((prev) =>
        prev.map((item) => (item.id === match.id ? updated : item))
      );
    } catch (err) {
      setError(err.message);
    }
  }

  function exportCsv() {
    window.open(api.exportMatchesCsvUrl(), "_blank");
  }

  const pendingCount = matches.filter((m) => !m.notified).length;
  const selected = matches.find((m) => m.id === selectedId);

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Matches</h2>
          <p className="muted">Wishlist hits from inventory scrapes and new entries</p>
        </div>
        <div className="toolbar">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search customer, stock, model…"
          />
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={unhandledOnly}
              onChange={(e) => setUnhandledOnly(e.target.checked)}
            />
            Unhandled only
          </label>
          <button className="btn" onClick={exportCsv}>
            Export CSV
          </button>
          <button className="btn" onClick={loadMatches} disabled={loading}>
            Refresh
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="stats">
        <div className="stat">
          <div className="label">Total matches</div>
          <div className="value">{matches.length}</div>
        </div>
        <div className="stat">
          <div className="label">Needs attention</div>
          <div className="value">{pendingCount}</div>
        </div>
      </div>

      {selected && (
        <div className="detail-card">
          <div className="detail-card-header">
            <h3>Match details</h3>
            <button className="btn btn-ghost" onClick={() => setSelectedId(null)}>
              Close
            </button>
          </div>
          <div className="detail-grid">
            <div>
              <div className="detail-label">Customer</div>
              <div>{selected.customer_name}</div>
            </div>
            <div>
              <div className="detail-label">Contact</div>
              <div>
                {selected.phone_or_email?.includes("@") ? (
                  <a href={`mailto:${selected.phone_or_email}`}>
                    {selected.phone_or_email}
                  </a>
                ) : (
                  <a href={`tel:${selected.phone_or_email.replace(/\D/g, "")}`}>
                    {selected.phone_or_email}
                  </a>
                )}
              </div>
            </div>
            <div>
              <div className="detail-label">Wanted</div>
              <div>{selected.desired_model}</div>
            </div>
            <div>
              <div className="detail-label">Bike found</div>
              <div>
                {selected.year} {selected.model_name}
                {selected.color ? ` · ${selected.color}` : ""}
              </div>
            </div>
            <div>
              <div className="detail-label">Stock #</div>
              <div>{selected.stock_number}</div>
            </div>
            <div>
              <div className="detail-label">Matched</div>
              <div>{formatDate(selected.matched_date)}</div>
            </div>
            {selected.customer_notes && (
              <div className="detail-full">
                <div className="detail-label">Customer notes</div>
                <div>{selected.customer_notes}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {loading ? (
        <div className="empty">Loading matches…</div>
      ) : matches.length === 0 ? (
        <div className="empty">
          No matches yet. Add wishlist entries or run a scrape.
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Matched</th>
                <th>Customer</th>
                <th>Wanted</th>
                <th>Bike found</th>
                <th>Stock #</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((match) => (
                <tr
                  key={match.id}
                  className={selectedId === match.id ? "row-selected" : "row-clickable"}
                  onClick={() => setSelectedId(match.id)}
                >
                  <td>{formatDate(match.matched_date)}</td>
                  <td>
                    <strong>{match.customer_name}</strong>
                    <div className="muted" style={{ fontSize: "0.85rem" }}>
                      {match.phone_or_email}
                    </div>
                  </td>
                  <td>{match.desired_model}</td>
                  <td>
                    {match.year} {match.model_name}
                    {match.color ? ` · ${match.color}` : ""}
                  </td>
                  <td>{match.stock_number}</td>
                  <td>
                    <span
                      className={`badge ${match.notified ? "badge-done" : "badge-new"}`}
                    >
                      {match.notified ? "Handled" : "New"}
                    </span>
                  </td>
                  <td>
                    <button
                      className={
                        match.notified ? "btn btn-ghost" : "btn btn-success"
                      }
                      onClick={(e) => toggleNotified(match, e)}
                    >
                      {match.notified ? "Mark unhandled" : "Mark notified"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
