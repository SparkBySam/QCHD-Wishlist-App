The hero of Dashboard — full-width data table with clickable sortable column headers (stock #, model, year, color) and optional row-click for expandable detail (Matches, Wishlist).

```jsx
<DataTable
  columns={[
    { key: "stock_number", label: "Stock #", sortable: true },
    { key: "model_name", label: "Model", sortable: true },
    { key: "year", label: "Year", sortable: true },
    { key: "color", label: "Color", render: (r) => r.color || "—" },
  ]}
  rows={inventory}
  sortKey={sortKey}
  sortDir={sortDir}
  onSort={handleSort}
/>
```

Sortable header shows a ▲/▼ caret for the active sort column. Pass `onRowClick` + `selectedId` to make rows clickable (Matches row → detail card).
