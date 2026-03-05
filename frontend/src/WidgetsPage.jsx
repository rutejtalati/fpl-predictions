import { useEffect, useMemo, useState } from "react";

function getCurrentSeason() {
  const now = new Date();
  const year = now.getUTCFullYear();
  if (year < 2025) {
    return 2025;
  }
  return year;
}

function getLeagueOptions() {
  return [
    { code: "EPL", name: "Premier League", leagueId: 39 },
    { code: "LALIGA", name: "LaLiga", leagueId: 140 },
    { code: "SERIEA", name: "Serie A", leagueId: 135 },
    { code: "LIGUE1", name: "Ligue 1", leagueId: 61 },
  ];
}

function getTeamOptionsByLeague() {
  return {
    EPL: [
      { name: "Arsenal", id: 42 },
      { name: "Chelsea", id: 49 },
      { name: "Liverpool", id: 40 },
      { name: "Manchester City", id: 50 },
      { name: "Manchester United", id: 33 },
      { name: "Tottenham", id: 47 },
    ],
    LALIGA: [
      { name: "Barcelona", id: 529 },
      { name: "Real Madrid", id: 541 },
      { name: "Atletico Madrid", id: 530 },
      { name: "Sevilla", id: 536 },
      { name: "Real Sociedad", id: 548 },
    ],
    SERIEA: [
      { name: "Inter", id: 505 },
      { name: "Milan", id: 489 },
      { name: "Juventus", id: 496 },
      { name: "Napoli", id: 492 },
      { name: "Roma", id: 497 },
    ],
    LIGUE1: [
      { name: "PSG", id: 85 },
      { name: "Marseille", id: 81 },
      { name: "Monaco", id: 91 },
      { name: "Lille", id: 79 },
      { name: "Lyon", id: 80 },
    ],
  };
}

function findLeagueByCode(code, options) {
  let index = 0;
  while (index < options.length) {
    if (options[index].code === code) {
      return options[index];
    }
    index += 1;
  }
  return options[0];
}

function findDefaultTeamId(code, teamOptionsByLeague) {
  const teams = teamOptionsByLeague[code] || [];
  if (teams.length === 0) {
    return "";
  }
  return String(teams[0].id);
}

export default function WidgetsPage({ onBack }) {
  const widgetApiKey = import.meta.env.VITE_APISPORTS_KEY || "";
  const leagueOptions = useMemo(getLeagueOptions, []);
  const teamOptionsByLeague = useMemo(getTeamOptionsByLeague, []);
  const [season] = useState(getCurrentSeason());
  const [leagueCode, setLeagueCode] = useState("EPL");
  const [teamId, setTeamId] = useState(findDefaultTeamId("EPL", teamOptionsByLeague));

  useEffect(function syncTeamOnLeagueChange() {
    setTeamId(findDefaultTeamId(leagueCode, teamOptionsByLeague));
  }, [leagueCode, teamOptionsByLeague]);

  function handleLeagueChange(event) {
    setLeagueCode(event.target.value);
  }

  function handleTeamChange(event) {
    setTeamId(event.target.value);
  }

  function renderLeagueOption(option) {
    return (
      <option key={option.code} value={option.code}>
        {option.name}
      </option>
    );
  }

  function renderTeamOption(option) {
    return (
      <option key={option.id} value={String(option.id)}>
        {option.name}
      </option>
    );
  }

  const selectedLeague = findLeagueByCode(leagueCode, leagueOptions);
  const leagueTeams = teamOptionsByLeague[leagueCode] || [];

  return (
    <section className="panel widgetsPanel">
      <div className="row widgetsHeaderRow" style={{ justifyContent: "space-between" }}>
        <h2>Football Widgets</h2>
        <button type="button" className="btn ghost" onClick={onBack}>
          Home
        </button>
      </div>

      {!widgetApiKey ? (
        <div className="error">
          Missing <code>VITE_APISPORTS_KEY</code>. Add it in your frontend env file to load widgets.
        </div>
      ) : null}

      <div className="widgetsControls">
        <label>
          League
          <select value={leagueCode} onChange={handleLeagueChange}>
            {leagueOptions.map(renderLeagueOption)}
          </select>
        </label>
        <label>
          Team
          <select value={teamId} onChange={handleTeamChange}>
            {leagueTeams.map(renderTeamOption)}
          </select>
        </label>
      </div>

      <api-sports-widget
        data-type="config"
        data-key={widgetApiKey}
        data-sport="football"
        data-theme="MyTheme"
        data-lang="custom"
        data-custom-lang="/lang/custom.json"
        data-show-logos="true"
        data-timezone="utc"
      />

      <div className="widgetsTwoColumn">
        <div className="widgetsMainColumn">
          <div className="widgetCard compactWidgetCard">
            <div className="widgetCardTitle">Matches</div>
            <div className="widgetCardBody">
              <api-sports-widget
                key={`games-${selectedLeague.leagueId}-${season}`}
                data-type="games"
                data-league={String(selectedLeague.leagueId)}
                data-season={String(season)}
                data-target-game="modal"
              />
            </div>
          </div>

          <div className="widgetCard compactWidgetCard">
            <div className="widgetCardTitle">Table</div>
            <div className="widgetCardBody">
              <api-sports-widget
                key={`standings-${selectedLeague.leagueId}-${season}`}
                data-type="standings"
                data-league={String(selectedLeague.leagueId)}
                data-season={String(season)}
                data-target-team="modal"
              />
            </div>
          </div>
        </div>

        <aside className="widgetsSideColumn">
          <div className="widgetCard compactWidgetCard">
            <div className="widgetCardTitle">Team</div>
            <div className="widgetCardBody">
              <api-sports-widget
                key={`team-${teamId}-${selectedLeague.leagueId}-${season}`}
                data-type="team"
                data-team={String(teamId)}
                data-league={String(selectedLeague.leagueId)}
                data-season={String(season)}
                data-target-player="modal"
              />
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
