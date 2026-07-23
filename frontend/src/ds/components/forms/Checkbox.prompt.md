Labeled checkbox for toolbar filters (e.g. the Matches view's "Unhandled only" toggle).

```jsx
<Checkbox label="Unhandled only" checked={unhandledOnly} onChange={setUnhandledOnly} />
```

Uses the browser-native checkbox with `accent-color: var(--accent)` — no custom-drawn box.
