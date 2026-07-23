import React from "react";

export function DetailCard({ title, onClose, children }) {
  return (
    <div className="detail-card">
      <div className="detail-card-header">
        <h3>{title}</h3>
        {onClose && (
          <button className="btn btn-ghost" onClick={onClose}>
            Close
          </button>
        )}
      </div>
      <div className="detail-grid">{children}</div>
    </div>
  );
}

export function DetailField({ label, full = false, children }) {
  return (
    <div className={full ? "detail-full" : ""}>
      <div className="detail-label">{label}</div>
      <div>{children}</div>
    </div>
  );
}
