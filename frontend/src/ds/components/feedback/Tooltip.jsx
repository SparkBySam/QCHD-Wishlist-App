import React from "react";

export function Tooltip({ label, children }) {
  return (
    <span className="qchd-tooltip-wrap" tabIndex={0}>
      {children}
      <span className="qchd-tooltip">{label}</span>
    </span>
  );
}
