export default function SearchBar({ value, onChange, placeholder = "Search…" }) {
  return (
    <input
      className="search-input"
      type="search"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  );
}
