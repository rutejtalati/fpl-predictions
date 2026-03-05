function formatNumber(value) {
  return Number(value).toFixed(2);
}

export default function PredictionsTable({ rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Team</th>
            <th>Pos</th>
            <th>Price</th>
            <th>Predicted</th>
            <th>Chance %</th>
            <th>Form</th>
            <th>PPG</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(function renderRow(row) {
            return (
              <tr key={row.id}>
                <td>{row.name}</td>
                <td>{row.team}</td>
                <td>{row.position}</td>
                <td>{formatNumber(row.price)}</td>
                <td>{formatNumber(row.predicted_points)}</td>
                <td>{row.chance_playing}</td>
                <td>{formatNumber(row.form)}</td>
                <td>{formatNumber(row.points_per_game)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
