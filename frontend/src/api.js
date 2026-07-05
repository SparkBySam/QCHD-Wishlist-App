const API_BASE = "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  getInventory: (activeOnly = true, search = "") => {
    const params = new URLSearchParams({ active_only: String(activeOnly) });
    if (search.trim()) params.set("search", search.trim());
    return request(`/api/inventory?${params}`);
  },

  triggerScrape: () =>
    request("/api/inventory/scrape", { method: "POST" }),

  getScrapeStatus: () => request("/api/inventory/scrape/status"),

  getAlertsConfig: () => request("/api/inventory/alerts/config"),

  getNotifications: (unreadOnly = false) =>
    request(`/api/inventory/notifications?unread_only=${unreadOnly}`),

  markNotificationRead: (id) =>
    request(`/api/inventory/notifications/${id}/read`, { method: "PATCH" }),

  getWishlist: (search = "", status = "") => {
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    if (status) params.set("status", status);
    const qs = params.toString();
    return request(`/api/wishlist${qs ? `?${qs}` : ""}`);
  },

  createWishlistEntry: (payload) =>
    request("/api/wishlist", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateWishlistEntry: (id, payload) =>
    request(`/api/wishlist/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  fulfillWishlistEntry: (id) =>
    request(`/api/wishlist/${id}/fulfill`, { method: "PATCH" }),

  deleteWishlistEntry: (id) =>
    request(`/api/wishlist/${id}`, { method: "DELETE" }),

  getMatches: (search = "", unhandledOnly = false) => {
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    if (unhandledOnly) params.set("unhandled_only", "true");
    const qs = params.toString();
    return request(`/api/matches${qs ? `?${qs}` : ""}`);
  },

  exportMatchesCsvUrl: () => `${API_BASE}/api/matches/export`,

  setMatchNotified: (id, notified) =>
    request(`/api/matches/${id}/notified`, {
      method: "PATCH",
      body: JSON.stringify({ notified }),
    }),
};
