import React from "react";

export function StatCard({ label, value, accent = false }) {
  return (
    <div className="stat">
      <div className="label">{label}</div>
      <div className={accent ? "value accent" : "value"}>{value}</div>
    </div>
  );
}
