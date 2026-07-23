Top-level card shell — every view (Dashboard, Wishlist, Matches) renders as one Panel.

```jsx
<Panel title="Inventory Dashboard" subtitle="Active bikes on the lot"
  toolbar={<><SearchBar .../><Button variant="primary">Scrape Now</Button></>}>
  {/* stats, banners, table */}
</Panel>
```

Header is optional — omit `title`/`toolbar` for a bare card (see DetailCard for a nested example).
