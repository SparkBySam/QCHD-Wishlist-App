Top-level view switcher in the app header — the only navigation the app has (3 views, no sidebar).

```jsx
<NavTabs
  items={[{id:"dashboard", label:"Dashboard"}, {id:"wishlist", label:"Wishlist"}, {id:"matches", label:"Matches"}]}
  activeId={view}
  onChange={setView}
/>
```

Active tab fills orange; inactive tabs are muted text that lighten on hover.
