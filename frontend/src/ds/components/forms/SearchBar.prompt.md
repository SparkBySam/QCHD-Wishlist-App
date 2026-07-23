Toolbar search input — appears in Dashboard, Wishlist, and Matches, always as the first toolbar item.

```jsx
<SearchBar value={search} onChange={setSearch} placeholder="Search stock, model, color…" />
```

Controlled component; `onChange` receives the raw string (not an event).
