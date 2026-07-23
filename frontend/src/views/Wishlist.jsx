import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import ContactWithCopy from "../components/ContactWithCopy";
import {
  Badge,
  Banner,
  Button,
  Field,
  SearchBar,
} from "../ds";
import { formatDate } from "../utils/dates";

const emptyForm = {
  customer_name: "",
  phone_or_email: "",
  desired_model: "",
  desired_year_min: new Date().getFullYear() - 5,
  desired_year_max: new Date().getFullYear() + 1,
  desired_color: "",
  desired_condition: "",
  notes: "",
  status: "active",
};

function conditionTone(condition) {
  if (condition === "new") return "condition-new";
  if (condition === "used") return "condition-used";
  return "condition-unknown";
}

export default function Wishlist() {
  const [entries, setEntries] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [conditionFilter, setConditionFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadEntries = useCallback(async () => {
    setError("");
    try {
      const data = await api.getWishlist(search, statusFilter, conditionFilter);
      setEntries(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, conditionFilter]);

  useEffect(() => {
    loadEntries();
  }, [loadEntries]);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function startEdit(entry) {
    setEditingId(entry.id);
    setForm({
      customer_name: entry.customer_name,
      phone_or_email: entry.phone_or_email,
      desired_model: entry.desired_model,
      desired_year_min: entry.desired_year_min,
      desired_year_max: entry.desired_year_max,
      desired_color: entry.desired_color || "",
      desired_condition: entry.desired_condition || "",
      notes: entry.notes || "",
      status: entry.status,
    });
  }

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccessMessage("");

    const payload = {
      ...form,
      desired_year_min: Number(form.desired_year_min),
      desired_year_max: Number(form.desired_year_max),
      desired_color: form.desired_color.trim() || null,
      desired_condition: form.desired_condition || null,
      notes: form.notes.trim() || null,
    };

    try {
      let result;
      if (editingId) {
        result = await api.updateWishlistEntry(editingId, payload);
      } else {
        result = await api.createWishlistEntry(payload);
      }
      if (result.new_matches > 0) {
        setSuccessMessage(
          `Saved. ${result.new_matches} immediate match${result.new_matches === 1 ? "" : "es"} found in current inventory.`
        );
      } else {
        setSuccessMessage("Saved. No immediate matches in current inventory.");
      }
      resetForm();
      await loadEntries();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleFulfill(id) {
    try {
      await api.fulfillWishlistEntry(id);
      await loadEntries();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this wishlist entry?")) return;
    try {
      await api.deleteWishlistEntry(id);
      if (editingId === id) resetForm();
      await loadEntries();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Customer Wishlist</h2>
          <p className="muted">New entries are matched against current inventory immediately</p>
        </div>
        <div className="toolbar">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search customer, model, notes…"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter by status"
          >
            <option value="">All statuses</option>
            <option value="active">active</option>
            <option value="fulfilled">fulfilled</option>
            <option value="cancelled">cancelled</option>
          </select>
          <select
            value={conditionFilter}
            onChange={(e) => setConditionFilter(e.target.value)}
            aria-label="Filter by condition"
          >
            <option value="">All conditions</option>
            <option value="new">New</option>
            <option value="used">Used</option>
          </select>
        </div>
      </div>

      {error && <Banner tone="error">{error}</Banner>}
      {successMessage && <Banner tone="success">{successMessage}</Banner>}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <Field label="Customer name">
            <input
              required
              value={form.customer_name}
              onChange={(e) => updateField("customer_name", e.target.value)}
            />
          </Field>
          <Field label="Phone or email">
            <input
              required
              value={form.phone_or_email}
              onChange={(e) => updateField("phone_or_email", e.target.value)}
            />
          </Field>
          <Field label="Desired model(s)" full>
            <textarea
              required
              rows={2}
              placeholder="One per line or comma-separated, e.g. Fat Boy, Street Glide, FLHX"
              value={form.desired_model}
              onChange={(e) => updateField("desired_model", e.target.value)}
            />
          </Field>
          <Field label="Year min">
            <input
              required
              type="number"
              value={form.desired_year_min}
              onChange={(e) => updateField("desired_year_min", e.target.value)}
            />
          </Field>
          <Field label="Year max">
            <input
              required
              type="number"
              value={form.desired_year_max}
              onChange={(e) => updateField("desired_year_max", e.target.value)}
            />
          </Field>
          <Field label="Desired color (optional)">
            <input
              placeholder="Leave blank for any"
              value={form.desired_color}
              onChange={(e) => updateField("desired_color", e.target.value)}
            />
          </Field>
          <Field label="New / Used">
            <select
              value={form.desired_condition}
              onChange={(e) => updateField("desired_condition", e.target.value)}
            >
              <option value="">Any</option>
              <option value="new">New</option>
              <option value="used">Used</option>
            </select>
          </Field>
          <Field label="Status">
            <select
              value={form.status}
              onChange={(e) => updateField("status", e.target.value)}
            >
              <option value="active">active</option>
              <option value="fulfilled">fulfilled</option>
              <option value="cancelled">cancelled</option>
            </select>
          </Field>
          <Field label="Notes" full>
            <textarea
              rows={2}
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
            />
          </Field>
        </div>
        <div className="toolbar">
          <Button variant="primary" type="submit" disabled={saving}>
            {saving
              ? "Saving…"
              : editingId
                ? "Update Entry"
                : "Add Wishlist Entry"}
          </Button>
          {editingId && (
            <Button type="button" onClick={resetForm}>
              Cancel edit
            </Button>
          )}
        </div>
      </form>

      {loading ? (
        <div className="empty">Loading wishlist…</div>
      ) : entries.length === 0 ? (
        <div className="empty">No wishlist entries{search || conditionFilter || statusFilter ? " matching your filters" : ""}.</div>
      ) : (
        <div className="table-wrap table-spaced">
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Contact</th>
                <th>Looking for</th>
                <th>Years</th>
                <th>Color</th>
                <th>Condition</th>
                <th>Status</th>
                <th>Added</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td>
                    <strong>{entry.customer_name}</strong>
                    {entry.notes && (
                      <div className="muted" style={{ fontSize: "var(--text-sm)" }}>
                        {entry.notes}
                      </div>
                    )}
                  </td>
                  <td>
                    <ContactWithCopy contact={entry.phone_or_email} />
                  </td>
                  <td>{entry.desired_model}</td>
                  <td>
                    {entry.desired_year_min}–{entry.desired_year_max}
                  </td>
                  <td>{entry.desired_color || "Any"}</td>
                  <td>
                    {entry.desired_condition ? (
                      <Badge tone={conditionTone(entry.desired_condition)}>
                        {entry.desired_condition}
                      </Badge>
                    ) : (
                      "Any"
                    )}
                  </td>
                  <td>
                    <Badge tone={entry.status}>{entry.status}</Badge>
                  </td>
                  <td>{formatDate(entry.date_added)}</td>
                  <td>
                    <div className="actions">
                      <Button variant="ghost" onClick={() => startEdit(entry)}>
                        Edit
                      </Button>
                      {entry.status === "active" && (
                        <Button variant="success" onClick={() => handleFulfill(entry.id)}>
                          Fulfill
                        </Button>
                      )}
                      <Button variant="danger" onClick={() => handleDelete(entry.id)}>
                        Delete
                      </Button>
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
