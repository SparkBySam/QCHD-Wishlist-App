Centered confirm dialog over a blurred scrim. **Intentional addition** — the source app uses `window.confirm()` for delete confirmation (see Wishlist.jsx `handleDelete`); this component gives that same moment an on-brand look when a designer wants to move off the native browser dialog.

```jsx
<Modal
  open={confirmOpen}
  title="Delete this wishlist entry?"
  actions={<>
    <Button variant="ghost" onClick={close}>Cancel</Button>
    <Button variant="danger" onClick={confirmDelete}>Delete</Button>
  </>}
  onClose={close}
>
  This can't be undone.
</Modal>
```

Click the scrim or call `onClose` to dismiss; clicking inside the modal body does not close it.
