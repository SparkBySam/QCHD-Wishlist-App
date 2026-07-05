import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import SearchBar from "../components/SearchBar";

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export default function Dashboard() {
  const [inventory, setInventory] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [scrapeStatus, setScrapeStatus] = useState(null);
  const [alertsConfig, setAlertsConfig] = useState(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState("");
  const [scrapeMessage, setScrapeMessage] = useState("");
  const pollRef = useRef(null);

  const loadData = useCallback(async () => {
    setError("");
    try {
      const [items, notes, status, alerts] = await Promise.all([
        api.getInventory(true, search),
        api.getNotifications(true),
        api.getScrapeStatus(),
        api.getAlertsConfig(),
      ]);
      setInventory(items);
      setNotifications(notes);
      setScrapeStatus(status);
      setAlertsConfig(alerts);
      setScraping(status.scrape_status === "running");
      if (status.scrape_status === "success" && status.scrape_message) {
        setScrapeMessage(status.scrape_message);
      }
      if (status.scrape_status === "error" && status.scrape_message) {
        setError(status.scrape_message);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  function startPolling() {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const status = await api.getScrapeStatus();
        setScrapeStatus(status);
        if (status.scrape_status === "running") {
          setScraping(true);
          return;
        }
        clearInterval(pollRef.current);
        pollRef.current = null;
        setScraping(false);
        if (status.scrape_status === "success") {
          setScrapeMessage(status.scrape_message || "Scrape completed.");
          setError("");
        } else if (status.scrape_status === "error") {
          setError(status.scrape_message || "Scrape failed.");
        }
        await loadData();
      } catch (err) {
        setError(err.message);
        setScraping(false);
        if (pollRef.current) clearInterval(pollRef.current);
      }
    }, 2000);
  }

  async function handleScrape() {
    setScraping(true);
    setError("");
    setScrapeMessage("");
    try {
      const result = await api.triggerScrape();
      setScrapeMessage(result.message);
      startPolling();
    } catch (err) {
      setError(err.message);
      setScraping(false);
    }
  }

  async function dismissNotification(id) {
    try {
      await api.markNotificationRead(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Inventory Dashboard</h2>
          <p className="muted">
            Active bikes on the lot
            {scrapeStatus?.last_scrape_at && (
              <> · Last scraped {formatDate(scrapeStatus.last_scrape_at)}</>
            )}
          </p>
        </div>
        <div className="toolbar">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search stock, model, color…"
          />
          <button className="btn" onClick={loadData} disabled={loading || scraping}>
            Refresh
          </button>
          <button
            className="btn btn-primary"
            onClick={handleScrape}
            disabled={scraping}
          >
            {scraping ? "Scraping…" : "Scrape Now"}
          </button>
        </div>
      </div>

      {scraping && (
        <div className="info-banner">
          <div className="spinner" aria-hidden="true" />
          Scrape in progress — this usually takes 2–5 minutes. You can keep using
          the app; results will refresh when done.
        </div>
      )}

      {error && <div className="error">{error}</div>}
      {scrapeMessage && !scraping && (
        <div className="success-banner">{scrapeMessage}</div>
      )}

      {alertsConfig && (alertsConfig.email || alertsConfig.sms) && (
        <div className="info-banner subtle">
          External alerts enabled:
          {alertsConfig.email && " email"}
          {alertsConfig.email && alertsConfig.sms && " +"}
          {alertsConfig.sms && " SMS"}
        </div>
      )}

      {notifications.length > 0 && (
        <div className="notifications">
          <h3>New match notifications</h3>
          <ul>
            {notifications.map((note) => (
              <li key={note.id}>
                {note.message}{" "}
                <button
                  className="btn btn-ghost"
                  onClick={() => dismissNotification(note.id)}
                >
                  Dismiss
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="stats">
        <div className="stat">
          <div className="label">Active inventory</div>
          <div className="value">{inventory.length}</div>
        </div>
        <div className="stat">
          <div className="label">Unread notifications</div>
          <div className="value">{notifications.length}</div>
        </div>
      </div>

      {loading ? (
        <div className="empty">Loading inventory…</div>
      ) : inventory.length === 0 ? (
        <div className="empty">
          No active inventory{search ? " matching your search" : ""}.{" "}
          {!search && (
            <>
              Click <strong>Scrape Now</strong> to pull the latest bikes.
            </>
          )}
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Stock #</th>
                <th>Model</th>
                <th>Year</th>
                <th>Color</th>
                <th>First Seen</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item) => (
                <tr key={item.id}>
                  <td>{item.stock_number}</td>
                  <td>{item.model_name}</td>
                  <td>{item.year}</td>
                  <td>{item.color || "—"}</td>
                  <td>{formatDate(item.date_first_seen)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
