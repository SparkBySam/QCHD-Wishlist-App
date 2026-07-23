Label + control wrapper for the wishlist entry form — always used inside a `.form-grid` (auto-fit column grid, defined in shared.css).

```jsx
<div className="form-grid">
  <Field label="Customer name"><input required value={name} onChange={...} /></Field>
  <Field label="Notes" full><textarea rows={2} value={notes} onChange={...} /></Field>
</div>
```

`full` spans all grid columns — reserve for notes/long text.
