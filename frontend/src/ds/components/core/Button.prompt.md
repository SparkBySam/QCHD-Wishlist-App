Primary, success, danger, and ghost action button — the single most-used primitive in the app (toolbars, table row actions, form submits).

```jsx
<Button variant="primary">Scrape Now</Button>
<Button variant="success" size="sm">Mark notified</Button>
<Button variant="danger" size="sm">Delete</Button>
<Button variant="ghost">Cancel edit</Button>
```

Variants: `default` (neutral surface, most toolbar buttons), `primary` (orange, one per view — the main action), `success` (soft green, positive/confirm actions like "Mark notified"), `danger` (soft red, destructive actions), `ghost` (borderless, secondary/dismiss actions). `size="sm"` for dense table-row actions. `disabled` dims to 55% opacity and blocks pointer events.
