import { useState } from "react";
import { NavTabs } from "./ds";
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
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            QC
          </div>
          <div>
            <h1>Bike Wishlist Tracker</h1>
            <p>Match dealership inventory against customer wishlists</p>
          </div>
        </div>
        <NavTabs items={VIEWS} activeId={view} onChange={setView} />
      </header>

      {view === "dashboard" && <Dashboard />}
      {view === "wishlist" && <Wishlist />}
      {view === "matches" && <Matches />}
    </div>
  );
}
