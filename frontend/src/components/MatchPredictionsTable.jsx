function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatTopScores(topScores) {
  if (!Array.isArray(topScores) || topScores.length === 0) {
    return "-";
  }
  return topScores
    .map(function mapScore(row) {
      return `${row.score} (${(Number(row.p) * 100).toFixed(1)}%)`;
    })
    .join(", ");
}

export default function MatchPredictionsTable({ rows }) {
  return (
    <div className="table-wrap card">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Home</th>
            <th>Away</th>
            <th>xG Home</th>
            <th>xG Away</th>
            <th>P(Home)</th>
            <th>P(Draw)</th>
            <th>P(Away)</th>
            <th>Most Likely Score</th>
            <th>Top 3 Scores</th>
            <th>Over 2.5</th>
            <th>BTTS</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(function renderRow(row, index) {
            return (
              <tr key={`${row.date}-${row.home}-${row.away}-${index}`}>
                <td>{new Date(row.date).toLocaleDateString()}</td>
                <td>{row.home}</td>
                <td>{row.away}</td>
                <td>{Number(row.xg_home).toFixed(2)}</td>
                <td>{Number(row.xg_away).toFixed(2)}</td>
                <td>{formatPercent(row.p_home)}</td>
                <td>{formatPercent(row.p_draw)}</td>
                <td>{formatPercent(row.p_away)}</td>
                <td>{row.most_likely_score}</td>
                <td>{formatTopScores(row.top_scores)}</td>
                <td>{formatPercent(row.over25_p)}</td>
                <td>{formatPercent(row.btts_p)}</td>
                <td>{formatPercent(row.confidence)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
