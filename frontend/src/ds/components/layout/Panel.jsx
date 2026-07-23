import React from "react";

export function Panel({ title, subtitle, toolbar, children }) {
  return (
    <div className="panel">
      {(title || toolbar) && (
        <div className="panel-header">
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p className="muted" style={{ margin: "0.25rem 0 0" }}>{subtitle}</p>}
          </div>
          {toolbar && <div className="toolbar">{toolbar}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
