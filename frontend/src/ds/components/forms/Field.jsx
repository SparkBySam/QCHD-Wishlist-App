import React from "react";

export function Field({ label, full = false, children }) {
  return (
    <label className={full ? "full" : ""}>
      {label}
      {children}
    </label>
  );
}
