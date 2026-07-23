Full-width inline banner — request errors, save confirmations, scrape-in-progress state, "external alerts enabled" note.

```jsx
<Banner tone="error">Failed to reach the scraper service.</Banner>
<Banner tone="success">Saved. 2 immediate matches found.</Banner>
<Banner tone="info"><Spinner /> Scrape in progress — 2–5 minutes.</Banner>
<Banner tone="subtle">External alerts enabled: email + SMS</Banner>
```

`warning` tone is reused for the amber "new match notifications" list (see the notifications block in the Dashboard UI kit). Banners stack above the stats row, in the order: error → success → info → subtle.
