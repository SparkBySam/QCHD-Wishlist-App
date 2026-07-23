/** Parse API datetimes. Backend stores UTC but often omits the Z suffix. */
export function parseApiDate(value) {
  if (!value) return null;
  if (value instanceof Date) return value;

  const raw = String(value).trim();
  if (!raw) return null;

  // Already has timezone (Z or ±HH:MM)
  if (/[zZ]$/.test(raw) || /[+-]\d{2}:\d{2}$/.test(raw)) {
    return new Date(raw);
  }

  // Naive ISO from API → treat as UTC
  return new Date(raw.includes("T") ? `${raw}Z` : `${raw.replace(" ", "T")}Z`);
}

export function formatDateTime(value) {
  const date = parseApiDate(value);
  if (!date || Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString();
}

export function formatDate(value) {
  const date = parseApiDate(value);
  if (!date || Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString();
}
