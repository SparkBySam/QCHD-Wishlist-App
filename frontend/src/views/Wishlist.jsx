import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import SearchBar from "../components/SearchBar";

const emptyForm = {
  customer_name: "",
  phone_or_email: "",
  desired_model: "",
  desired_year_min: new Date().getFullYear() - 5,
  desired_year_max: new Date().getFullYear() + 1,
  desired_color: "",
  notes: "",
  status: "active",
};

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString();
}

export default function Wishlist() {
  const [entries, setEntries] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadEntries = useCallback(async () => {
    setError("");
    try {
      const data = await api.getWishlist(search, statusFilter);
      setEntries(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

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
          >
            <option value="">All statuses</option>
            <option value="active">active</option>
            <option value="fulfilled">fulfilled</option>
            <option value="cancelled">cancelled</option>
          </select>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {successMessage && <div className="success-banner">{successMessage}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Customer name
            <input
              required
              value={form.customer_name}
              onChange={(e) => updateField("customer_name", e.target.value)}
            />
          </label>
          <label>
            Phone or email
            <input
              required
              value={form.phone_or_email}
              onChange={(e) => updateField("phone_or_email", e.target.value)}
            />
          </label>
          <label>
            Desired model
            <input
              required
              placeholder="e.g. Fat Boy, FLFB, Street Glide"
              value={form.desired_model}
              onChange={(e) => updateField("desired_model", e.target.value)}
            />
          </label>
          <label>
            Year min
            <input
              required
              type="number"
              value={form.desired_year_min}
              onChange={(e) => updateField("desired_year_min", e.target.value)}
            />
          </label>
          <label>
            Year max
            <input
              required
              type="number"
              value={form.desired_year_max}
              onChange={(e) => updateField("desired_year_max", e.target.value)}
            />
          </label>
          <label>
            Desired color (optional)
            <input
              placeholder="Leave blank for any"
              value={form.desired_color}
              onChange={(e) => updateField("desired_color", e.target.value)}
            />
          </label>
          <label>
            Status
            <select
              value={form.status}
              onChange={(e) => updateField("status", e.target.value)}
            >
              <option value="active">active</option>
              <option value="fulfilled">fulfilled</option>
              <option value="cancelled">cancelled</option>
            </select>
          </label>
          <label className="full">
            Notes
            <textarea
              rows={2}
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
            />
          </label>
        </div>
        <div className="toolbar">
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving
              ? "Saving…"
              : editingId
                ? "Update Entry"
                : "Add Wishlist Entry"}
          </button>
          {editingId && (
            <button className="btn" type="button" onClick={resetForm}>
              Cancel edit
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <div className="empty">Loading wishlist…</div>
      ) : entries.length === 0 ? (
        <div className="empty">No wishlist entries{search ? " matching your search" : ""}.</div>
      ) : (
        <div className="table-wrap" style={{ marginTop: "1.25rem" }}>
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Contact</th>
                <th>Looking for</th>
                <th>Years</th>
                <th>Color</th>
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
                      <div className="muted" style={{ fontSize: "0.85rem" }}>
                        {entry.notes}
                      </div>
                    )}
                  </td>
                  <td>{entry.phone_or_email}</td>
                  <td>{entry.desired_model}</td>
                  <td>
                    {entry.desired_year_min}–{entry.desired_year_max}
                  </td>
                  <td>{entry.desired_color || "Any"}</td>
                  <td>
                    <span className={`badge badge-${entry.status}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td>{formatDate(entry.date_added)}</td>
                  <td>
                    <div className="actions">
                      <button
                        className="btn btn-ghost"
                        onClick={() => startEdit(entry)}
                      >
                        Edit
                      </button>
                      {entry.status === "active" && (
                        <button
                          className="btn btn-success"
                          onClick={() => handleFulfill(entry.id)}
                        >
                          Fulfill
                        </button>
                      )}
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDelete(entry.id)}
                      >
                        Delete
                      </button>
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
