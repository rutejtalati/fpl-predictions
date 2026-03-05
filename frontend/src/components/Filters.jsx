function onInputChange(event, onChange) {
  const { name, value } = event.target;
  onChange(name, value);
}

export default function Filters({ filters, teams, onChange, onApply, onReset }) {
  return (
    <section className="filters">
      <div className="field">
        <label htmlFor="search">Search</label>
        <input
          id="search"
          name="search"
          type="text"
          value={filters.search}
          placeholder="Player name"
          onChange={(event) => onInputChange(event, onChange)}
        />
      </div>

      <div className="field">
        <label htmlFor="team_id">Team</label>
        <select
          id="team_id"
          name="team_id"
          value={filters.team_id}
          onChange={(event) => onInputChange(event, onChange)}
        >
          <option value="">All teams</option>
          {teams.map(function renderTeam(team) {
            return (
              <option key={team.id} value={team.id}>
                {team.short_name || team.name}
              </option>
            );
          })}
        </select>
      </div>

      <div className="field">
        <label htmlFor="position">Position</label>
        <select
          id="position"
          name="position"
          value={filters.position}
          onChange={(event) => onInputChange(event, onChange)}
        >
          <option value="">All positions</option>
          <option value="GK">GK</option>
          <option value="DEF">DEF</option>
          <option value="MID">MID</option>
          <option value="FWD">FWD</option>
        </select>
      </div>

      <div className="field">
        <label htmlFor="min_price">Min Price</label>
        <input
          id="min_price"
          name="min_price"
          type="number"
          step="0.1"
          value={filters.min_price}
          onChange={(event) => onInputChange(event, onChange)}
        />
      </div>

      <div className="field">
        <label htmlFor="max_price">Max Price</label>
        <input
          id="max_price"
          name="max_price"
          type="number"
          step="0.1"
          value={filters.max_price}
          onChange={(event) => onInputChange(event, onChange)}
        />
      </div>

      <div className="actions">
        <button type="button" onClick={onApply}>Apply</button>
        <button type="button" className="ghost" onClick={onReset}>Reset</button>
      </div>
    </section>
  );
}
