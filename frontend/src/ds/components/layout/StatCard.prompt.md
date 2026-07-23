Compact metric tile — always shown in a `.stats` grid (2–4 across) at the top of a view, below the panel header.

```jsx
<div className="stats">
  <StatCard label="Active inventory" value={128} />
  <StatCard label="Needs attention" value={4} accent />
</div>
```

`accent` colors the number orange — use sparingly, only for the one number that most needs a look (unhandled matches, unread notifications).
