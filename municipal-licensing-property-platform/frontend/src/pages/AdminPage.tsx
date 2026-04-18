import { getDiagnostics } from "../api/health";
import Layout from "../components/Layout";
import { useAsync } from "../hooks/useAsync";

export default function AdminPage() {
  const { data, error, loading } = useAsync(getDiagnostics, []);
  return (
    <Layout title="Diagnostics">
      {loading && <div>Loading…</div>}
      {error && <div className="error-box">{error}</div>}
      {data && <pre className="code-box">{JSON.stringify(data, null, 2)}</pre>}
    </Layout>
  );
}
