function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

export default function TableProjection({ rows }) {
  return (
    <div className="table-wrap card">
      <table>
        <thead>
          <tr>
            <th>Team</th>
            <th>Expected Points</th>
            <th>Expected Rank</th>
            <th>Most Likely Rank</th>
            <th>Rank Range (10-90%)</th>
            <th>Title Probability</th>
            <th>Top 4 Probability</th>
            <th>Relegation Probability</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(function renderRow(row) {
            return (
              <tr key={row.team}>
                <td>{row.team}</td>
                <td>{Number(row.expected_points).toFixed(2)}</td>
                <td>{Number(row.expected_rank).toFixed(2)}</td>
                <td>{row.most_likely_rank}</td>
                <td>{row.rank_range_10_90}</td>
                <td>{formatPercent(row.title_probability)}</td>
                <td>{formatPercent(row.top4_probability)}</td>
                <td>{formatPercent(row.relegation_probability)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
