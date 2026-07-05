import { useState } from "react";
import Dashboard from "./views/Dashboard";
import Wishlist from "./views/Wishlist";
import Matches from "./views/Matches";

const VIEWS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "wishlist", label: "Wishlist" },
  { id: "matches", label: "Matches" },
];

export default function App() {
  const [view, setView] = useState("dashboard");

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Bike Wishlist Tracker</h1>
          <p>Match dealership inventory against customer wishlists</p>
        </div>
        <nav className="nav">
          {VIEWS.map((item) => (
            <button
              key={item.id}
              className={view === item.id ? "active" : ""}
              onClick={() => setView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      {view === "dashboard" && <Dashboard />}
      {view === "wishlist" && <Wishlist />}
      {view === "matches" && <Matches />}
    </div>
  );
}
