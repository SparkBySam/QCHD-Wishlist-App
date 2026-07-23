import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import {
  Badge,
  Banner,
  Button,
  SearchBar,
  Spinner,
  StatCard,
} from "../ds";
import { formatDateTime, parseApiDate } from "../utils/dates";

const COLUMNS = [
  { key: "stock_number", label: "Stock #" },
  { key: "model_name", label: "Model" },
  { key: "year", label: "Year" },
  { key: "condition", label: "Condition" },
  { key: "color", label: "Color" },
  { key: "date_first_seen", label: "First Seen" },
];

function formatNextScrape(dueAt) {
  const due = parseApiDate(dueAt);
  if (!due) return null;
  if (due.getTime() <= Date.now()) return "due now";
  return formatDateTime(dueAt);
}

function conditionTone(condition) {
  if (condition === "new") return "condition-new";
  if (condition === "used") return "condition-used";
  return "condition-unknown";
}

function ConditionBadge({ condition }) {
  const value = (condition || "unknown").toLowerCase();
  const label = value === "unknown" ? "—" : value;
  return <Badge tone={conditionTone(value)}>{label}</Badge>;
}

function compareValues(a, b, key) {
  const left = a[key] ?? "";
  const right = b[key] ?? "";

  if (key === "year") {
    return Number(left) - Number(right);
  }
  if (key === "date_first_seen") {
    return (parseApiDate(left)?.getTime() || 0) - (parseApiDate(right)?.getTime() || 0);
  }
  return String(left).localeCompare(String(right), undefined, { sensitivity: "base" });
}

function SortableHeader({ column, sortKey, sortDir, onSort }) {
  const active = sortKey === column.key;
  const indicator = active ? (sortDir === "asc" ? " ↑" : " ↓") : "";

  return (
    <th>
      <button
        type="button"
        className={`sort-header${active ? " active" : ""}`}
        onClick={() => onSort(column.key)}
      >
        {column.label}
        <span className="sort-indicator" aria-hidden="true">
          {indicator || " ↕"}
        </span>
      </button>
    </th>
  );
}

export default function Dashboard() {
  const [inventory, setInventory] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [scrapeStatus, setScrapeStatus] = useState(null);
  const [alertsConfig, setAlertsConfig] = useState(null);
  const [search, setSearch] = useState("");
  const [conditionFilter, setConditionFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState("");
  const [scrapeMessage, setScrapeMessage] = useState("");
  const [sortKey, setSortKey] = useState("date_first_seen");
  const [sortDir, setSortDir] = useState("desc");
  const pollRef = useRef(null);

  const sortedInventory = useMemo(() => {
    const rows = [...inventory];
    rows.sort((a, b) => {
      const result = compareValues(a, b, sortKey);
      return sortDir === "asc" ? result : -result;
    });
    return rows;
  }, [inventory, sortKey, sortDir]);

  function handleSort(key) {
    if (sortKey === key) {
      setSortDir((dir) => (dir === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "date_first_seen" || key === "year" ? "desc" : "asc");
    }
  }

  const loadData = useCallback(async () => {
    setError("");
    try {
      const [items, notes, status, alerts] = await Promise.all([
        api.getInventory(true, search, conditionFilter),
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
  }, [search, conditionFilter]);

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

  async function clearAllNotifications() {
    try {
      await api.clearAllNotifications();
      setNotifications([]);
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
              <> · Last scraped {formatDateTime(scrapeStatus.last_scrape_at)}</>
            )}
            {scrapeStatus?.next_scrape_due_at &&
              scrapeStatus.scrape_status !== "running" && (
                <>
                  {" "}
                  · Next auto scrape {formatNextScrape(scrapeStatus.next_scrape_due_at)}
                </>
              )}
          </p>
        </div>
        <div className="toolbar">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search stock, model, color…"
          />
          <select
            value={conditionFilter}
            onChange={(e) => setConditionFilter(e.target.value)}
            aria-label="Filter by condition"
          >
            <option value="">All conditions</option>
            <option value="new">New</option>
            <option value="used">Used</option>
          </select>
          <Button onClick={loadData} disabled={loading || scraping}>
            Refresh
          </Button>
          <Button variant="primary" onClick={handleScrape} disabled={scraping}>
            {scraping ? "Scraping…" : "Scrape Now"}
          </Button>
        </div>
      </div>

      {scraping && (
        <Banner tone="info">
          <Spinner />
          Scrape in progress — this usually takes 2–5 minutes. You can keep using
          the app; results will refresh when done.
        </Banner>
      )}

      {error && <Banner tone="error">{error}</Banner>}
      {scrapeMessage && !scraping && (
        <Banner tone="success">{scrapeMessage}</Banner>
      )}

      {alertsConfig && (alertsConfig.email || alertsConfig.sms) && (
        <Banner tone="subtle">
          External alerts enabled:
          {alertsConfig.email && " email"}
          {alertsConfig.email && alertsConfig.sms && " +"}
          {alertsConfig.sms && " SMS"}
        </Banner>
      )}

      {notifications.length > 0 && (
        <div className="notifications">
          <div className="notifications-header">
            <h3>New match notifications ({notifications.length})</h3>
            <Button variant="ghost" onClick={clearAllNotifications}>
              Clear all
            </Button>
          </div>
          <ul>
            {notifications.map((note) => (
              <li key={note.id}>
                <span className="notification-text">{note.message}</span>
                <Button variant="ghost" onClick={() => dismissNotification(note.id)}>
                  Clear
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="stats">
        <StatCard label="Active inventory" value={inventory.length} />
        <StatCard
          label="New"
          value={inventory.filter((item) => item.condition === "new").length}
        />
        <StatCard
          label="Used"
          value={inventory.filter((item) => item.condition === "used").length}
        />
        <StatCard
          label="Unread notifications"
          value={notifications.length}
          accent={notifications.length > 0}
        />
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
                {COLUMNS.map((column) => (
                  <SortableHeader
                    key={column.key}
                    column={column}
                    sortKey={sortKey}
                    sortDir={sortDir}
                    onSort={handleSort}
                  />
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedInventory.map((item) => (
                <tr key={item.id}>
                  <td>{item.stock_number}</td>
                  <td>{item.model_name}</td>
                  <td>{item.year}</td>
                  <td>
                    <ConditionBadge condition={item.condition} />
                  </td>
                  <td>{item.color || "—"}</td>
                  <td>{formatDateTime(item.date_first_seen)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
