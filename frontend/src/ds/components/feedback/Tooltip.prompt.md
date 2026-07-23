Hover/focus tooltip. **Intentional addition** — not in the source app (which has no icon-only controls yet), but needed the moment any control loses its text label (e.g. an icon-only refresh button).

```jsx
<Tooltip label="Refresh inventory">
  <Button variant="ghost">⟳</Button>
</Tooltip>
```

Appears above the wrapped element on hover or keyboard focus.
