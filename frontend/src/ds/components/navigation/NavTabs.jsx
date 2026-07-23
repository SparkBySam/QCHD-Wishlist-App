import React from "react";

export function NavTabs({ items, activeId, onChange }) {
  return (
    <nav className="nav">
      {items.map((item) => (
        <button
          key={item.id}
          className={activeId === item.id ? "active" : ""}
          onClick={() => onChange(item.id)}
        >
          {item.label}
        </button>
      ))}
    </nav>
  );
}
