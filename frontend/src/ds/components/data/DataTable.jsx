import React from "react";

export function DataTable({ columns, rows, sortKey, sortDir = "asc", onSort, onRowClick, selectedId, rowKey = "id" }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={col.sortable ? () => onSort && onSort(col.key) : undefined}
                style={col.sortable ? { cursor: "pointer", userSelect: "none" } : undefined}
              >
                {col.label}
                {col.sortable && sortKey === col.key ? (sortDir === "asc" ? " ▲" : " ▼") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row[rowKey]}
              className={
                onRowClick ? (selectedId === row[rowKey] ? "row-selected" : "row-clickable") : undefined
              }
              onClick={onRowClick ? () => onRowClick(row) : undefined}
            >
              {columns.map((col) => (
                <td key={col.key}>{col.render ? col.render(row) : row[col.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
