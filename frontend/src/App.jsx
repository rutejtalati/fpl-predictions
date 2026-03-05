import { useMemo, useState } from "react";

import Header from "./components/Header";
import Home from "./pages/Home";
import EPL from "./pages/EPL";
import LaLiga from "./pages/LaLiga";
import Ligue1 from "./pages/Ligue1";
import SerieA from "./pages/SerieA";

export default function App() {
  const [page, setPage] = useState("home");

  const pageView = useMemo(
    function pickPage() {
      if (page === "epl" || page === "predictions") {
        return <EPL />;
      }
      if (page === "laliga") {
        return <LaLiga />;
      }
      if (page === "ligue1") {
        return <Ligue1 />;
      }
      if (page === "seriea") {
        return <SerieA />;
      }
      return <Home />;
    },
    [page]
  );

  return (
    <div className="app-shell">
      <Header currentPage={page} onNavigate={setPage} />
      {pageView}
    </div>
  );
}
