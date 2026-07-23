Inline expanded-detail card shown when a Matches (or Wishlist) row is clicked — customer contact + matched bike, in a labeled grid.

```jsx
<DetailCard title="Match details" onClose={() => setSelectedId(null)}>
  <DetailField label="Customer">Jane Rider</DetailField>
  <DetailField label="Contact"><a href="tel:...">(704) 555-0132</a></DetailField>
  <DetailField label="Notes" full>Prefers vivid black, cash deal.</DetailField>
</DetailCard>
```

`DetailField` labels are uppercase/muted per the shared `.detail-label` style; pass `full` for a field that should span the row (notes).
