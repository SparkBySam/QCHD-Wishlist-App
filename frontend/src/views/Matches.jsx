import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import ContactWithCopy from "../components/ContactWithCopy";
import {
  Badge,
  Banner,
  Button,
  Checkbox,
  DetailCard,
  DetailField,
  SearchBar,
  StatCard,
} from "../ds";
import { formatDateTime } from "../utils/dates";

function conditionTone(condition) {
  if (condition === "new") return "condition-new";
  if (condition === "used") return "condition-used";
  return "condition-unknown";
}

function ConditionBadge({ condition }) {
  const value = (condition || "unknown").toLowerCase();
  if (value === "unknown") return null;
  return <Badge tone={conditionTone(value)}>{value}</Badge>;
}

function bikeLabel(match) {
  const parts = [
    match.year,
    match.model_name,
    match.color ? `· ${match.color}` : null,
  ].filter(Boolean);
  return parts.join(" ");
}

export default function Matches() {
  const [matches, setMatches] = useState([]);
  const [search, setSearch] = useState("");
  const [unhandledOnly, setUnhandledOnly] = useState(true);
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
      setMatches((prev) => {
        if (unhandledOnly && updated.notified) {
          return prev.filter((item) => item.id !== match.id);
        }
        return prev.map((item) => (item.id === match.id ? updated : item));
      });
      if (unhandledOnly && updated.notified && selectedId === match.id) {
        setSelectedId(null);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function dismissMatch(match, event) {
    event?.stopPropagation();
    if (
      !window.confirm(
        `Mark this match for ${match.customer_name} as not interested? It will be removed from the list and won’t rematch this bike.`
      )
    ) {
      return;
    }
    try {
      await api.dismissMatch(match.id);
      setMatches((prev) => prev.filter((item) => item.id !== match.id));
      if (selectedId === match.id) {
        setSelectedId(null);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function expireMatch(match, event) {
    event?.stopPropagation();
    if (
      !window.confirm(
        `Expire this handled match for ${match.customer_name}? It will be removed immediately.`
      )
    ) {
      return;
    }
    try {
      await api.expireMatch(match.id);
      setMatches((prev) => prev.filter((item) => item.id !== match.id));
      if (selectedId === match.id) {
        setSelectedId(null);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function expireAllHandled() {
    const toExpire = matches.filter((m) => m.notified);
    if (toExpire.length === 0) return;
    const label = search.trim()
      ? `${toExpire.length} handled match${toExpire.length === 1 ? "" : "es"} in this list`
      : `all ${toExpire.length} handled match${toExpire.length === 1 ? "" : "es"}`;
    if (!window.confirm(`Expire ${label} now? They will be removed immediately.`)) {
      return;
    }
    try {
      const ids = search.trim() ? toExpire.map((m) => m.id) : null;
      await api.expireAllHandledMatches(ids);
      const expiredIds = new Set(toExpire.map((m) => m.id));
      setMatches((prev) => prev.filter((m) => !expiredIds.has(m.id)));
      if (selected?.notified && expiredIds.has(selected.id)) {
        setSelectedId(null);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  function exportCsv() {
    window.open(api.exportMatchesCsvUrl(), "_blank");
  }

  const pendingCount = matches.filter((m) => !m.notified).length;
  const handledCount = matches.filter((m) => m.notified).length;
  const selected = matches.find((m) => m.id === selectedId);

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Matches</h2>
          <p className="muted">
            Wishlist hits from inventory scrapes and new entries · Handled matches
            are removed after 7 days
          </p>
        </div>
        <div className="toolbar">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search customer, stock, model…"
          />
          <Checkbox
            label="Unhandled only"
            checked={unhandledOnly}
            onChange={setUnhandledOnly}
          />
          <Button onClick={exportCsv}>Export CSV</Button>
          {!unhandledOnly && handledCount > 0 && (
            <Button variant="danger" onClick={expireAllHandled}>
              Expire all handled
            </Button>
          )}
          <Button onClick={loadMatches} disabled={loading}>
            Refresh
          </Button>
        </div>
      </div>

      {error && <Banner tone="error">{error}</Banner>}

      <div className="stats">
        <StatCard label="Total matches" value={matches.length} />
        <StatCard
          label="Needs attention"
          value={pendingCount}
          accent={pendingCount > 0}
        />
      </div>

      {selected && (
        <DetailCard title="Match details" onClose={() => setSelectedId(null)}>
          <DetailField label="Customer">{selected.customer_name}</DetailField>
          <DetailField label="Contact">
            <ContactWithCopy contact={selected.phone_or_email} />
          </DetailField>
          <DetailField label="Wanted">{selected.desired_model}</DetailField>
          <DetailField label="Bike found">
            <span style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              {bikeLabel(selected)}
              <ConditionBadge condition={selected.condition} />
            </span>
          </DetailField>
          <DetailField label="Stock #">{selected.stock_number}</DetailField>
          <DetailField label="Matched">{formatDateTime(selected.matched_date)}</DetailField>
          {selected.customer_notes && (
            <DetailField label="Customer notes" full>
              {selected.customer_notes}
            </DetailField>
          )}
          <DetailField label="Actions" full>
            <div className="actions">
              {!selected.notified && (
                <Button variant="ghost" onClick={() => dismissMatch(selected)}>
                  Not interested
                </Button>
              )}
              {selected.notified && (
                <Button variant="danger" onClick={() => expireMatch(selected)}>
                  Expire now
                </Button>
              )}
            </div>
          </DetailField>
        </DetailCard>
      )}

      {loading ? (
        <div className="empty">Loading matches…</div>
      ) : matches.length === 0 ? (
        <div className="empty">
          {unhandledOnly
            ? "No unhandled matches. Uncheck “Unhandled only” to see handled history (kept for 7 days)."
            : "No matches yet. Add wishlist entries or run a scrape."}
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
                  <td>{formatDateTime(match.matched_date)}</td>
                  <td>
                    <strong>{match.customer_name}</strong>
                    <div className="muted contact-cell">
                      <ContactWithCopy contact={match.phone_or_email} stopRowClick />
                    </div>
                  </td>
                  <td>{match.desired_model}</td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                      <span>
                        {match.year} {match.model_name}
                        {match.color ? ` · ${match.color}` : ""}
                      </span>
                      <ConditionBadge condition={match.condition} />
                    </div>
                  </td>
                  <td>{match.stock_number}</td>
                  <td>
                    <Badge tone={match.notified ? "done" : "new"}>
                      {match.notified ? "Handled" : "New"}
                    </Badge>
                  </td>
                  <td>
                    <div className="actions">
                      <Button
                        variant={match.notified ? "ghost" : "success"}
                        onClick={(e) => toggleNotified(match, e)}
                      >
                        {match.notified ? "Mark unhandled" : "Mark notified"}
                      </Button>
                      {!match.notified && (
                        <Button
                          variant="ghost"
                          onClick={(e) => dismissMatch(match, e)}
                        >
                          Not interested
                        </Button>
                      )}
                      {match.notified && (
                        <Button
                          variant="danger"
                          onClick={(e) => expireMatch(match, e)}
                        >
                          Expire
                        </Button>
                      )}
                    </div>
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
