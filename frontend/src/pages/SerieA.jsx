import LeaguePredictionsPage from "./LeaguePredictionsPage";

export default function SerieA() {
  return <LeaguePredictionsPage title="Serie A" endpoint="/api/league/seriea/predictions" />;
}