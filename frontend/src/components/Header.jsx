const NAV_ITEMS = [
  { id: "home", label: "Home" },
  { id: "predictions", label: "Predictions" },
  { id: "epl", label: "EPL" },
  { id: "laliga", label: "La Liga" },
  { id: "ligue1", label: "Ligue 1" },
  { id: "seriea", label: "Serie A" },
];

export default function Header({ currentPage, onNavigate }) {
  return (
    <header className="app-header">
      <div>
        <h1>FPL Predictions</h1>
        <p>Baseline expected points from official FPL data</p>
      </div>
      <nav className="top-nav">
        {NAV_ITEMS.map(function renderNavItem(item) {
          const className = item.id === currentPage ? "nav-item active" : "nav-item";
          return (
            <button
              type="button"
              key={item.id}
              className={className}
              onClick={function onClick() {
                onNavigate(item.id);
              }}
            >
              {item.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
}
