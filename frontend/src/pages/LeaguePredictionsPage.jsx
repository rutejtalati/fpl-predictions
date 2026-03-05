import { useEffect, useState } from "react";

import { buildApiUrl, fetchJson } from "../api";
import MatchPredictionsTable from "../components/MatchPredictionsTable";
import TableProjection from "../components/TableProjection";

export default function LeaguePredictionsPage({ title, endpoint }) {
  const [matches, setMatches] = useState([]);
  const [tableProjection, setTableProjection] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(
    function loadLeaguePredictions() {
      let isMounted = true;

      async function run() {
        setLoading(true);
        setError("");
        try {
          const url = buildApiUrl(endpoint);
          const data = await fetchJson(url);
          if (!isMounted) {
            return;
          }
          setMatches(Array.isArray(data.matches) ? data.matches : []);
          setTableProjection(Array.isArray(data.table_projection) ? data.table_projection : []);
        } catch (err) {
          if (!isMounted) {
            return;
          }
          const message = err instanceof Error ? err.message : String(err);
          setError(message);
        } finally {
          if (isMounted) {
            setLoading(false);
          }
        }
      }

      run();

      return function cleanup() {
        isMounted = false;
      };
    },
    [endpoint]
  );

  return (
    <main className="page">
      <section className="card page-title-card">
        <h2>{title} Predictions</h2>
        <p>Monte Carlo match forecasts with season table projections.</p>
      </section>

      {loading ? <p className="status">Loading predictions...</p> : null}
      {error ? <p className="status error">{error}</p> : null}

      {!loading && !error ? <MatchPredictionsTable rows={matches} /> : null}
      {!loading && !error ? <TableProjection rows={tableProjection} /> : null}
    </main>
  );
}
