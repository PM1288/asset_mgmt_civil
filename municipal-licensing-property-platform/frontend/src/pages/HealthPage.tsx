import { getReadyHealth } from "../api/health";
import HealthPanel from "../components/HealthPanel";
import Layout from "../components/Layout";
import { useAsync } from "../hooks/useAsync";

export default function HealthPage() {
  const { data, error, loading } = useAsync(getReadyHealth, []);
  return (
    <Layout title="Health">
      {loading ? <div>Loading…</div> : <HealthPanel data={data} error={error} />}
    </Layout>
  );
}
