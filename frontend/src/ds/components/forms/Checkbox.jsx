import React from "react";

export function Checkbox({ label, checked, onChange }) {
  return (
    <label className="checkbox-label">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}
