import { useEffect, useState } from "react";

import { buildApiUrl, fetchJson } from "../api";
import Filters from "../components/Filters";
import PredictionsTable from "../components/PredictionsTable";

const DEFAULT_FILTERS = {
  search: "",
  team_id: "",
  position: "",
  min_price: "",
  max_price: "",
  limit: "200",
};

function cleanQuery(filters) {
  return {
    search: filters.search || undefined,
    team_id: filters.team_id || undefined,
    position: filters.position || undefined,
    min_price: filters.min_price || undefined,
    max_price: filters.max_price || undefined,
    limit: filters.limit || undefined,
  };
}

export default function Home() {
  const [teams, setTeams] = useState([]);
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadBootstrap() {
    const url = buildApiUrl("/fpl/bootstrap");
    const data = await fetchJson(url);
    setTeams(Array.isArray(data.teams) ? data.teams : []);
  }

  async function loadPredictions(activeFilters) {
    const url = buildApiUrl("/predictions", cleanQuery(activeFilters));
    const data = await fetchJson(url);
    setRows(Array.isArray(data.predictions) ? data.predictions : []);
  }

  async function loadAll(activeFilters) {
    setLoading(true);
    setError("");
    try {
      await Promise.all([loadBootstrap(), loadPredictions(activeFilters)]);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  function onFilterChange(name, value) {
    setFilters(function update(previous) {
      return { ...previous, [name]: value };
    });
  }

  function onApply() {
    loadPredictions(filters).catch(function onFail(err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
    });
  }

  function onReset() {
    setFilters(DEFAULT_FILTERS);
    loadPredictions(DEFAULT_FILTERS).catch(function onFail(err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
    });
  }

  useEffect(function onMount() {
    loadAll(DEFAULT_FILTERS);
  }, []);

  return (
    <main className="page">
      <Filters
        filters={filters}
        teams={teams}
        onChange={onFilterChange}
        onApply={onApply}
        onReset={onReset}
      />

      {loading ? <p className="status">Loading predictions...</p> : null}
      {error ? <p className="status error">{error}</p> : null}
      {!loading && !error ? <PredictionsTable rows={rows} /> : null}
    </main>
  );
}
