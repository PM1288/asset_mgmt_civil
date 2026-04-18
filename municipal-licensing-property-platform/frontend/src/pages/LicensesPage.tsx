import { useState } from "react";
import { createLicense, listLicenses } from "../api/licenses";
import Layout from "../components/Layout";
import LicenseList from "../components/LicenseList";
import { useAsync } from "../hooks/useAsync";

export default function LicensesPage() {
  const { data, error, loading, reload } = useAsync(listLicenses, []);
  const [form, setForm] = useState({
    application_number: "",
    property_id: "",
    license_type: "trade",
    applicant_name: "",
    applicant_contact: "",
    notes: ""
  });
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function submit() {
    setSubmitError(null);
    try {
      await createLicense(form);
      setForm({
        application_number: "",
        property_id: "",
        license_type: "trade",
        applicant_name: "",
        applicant_contact: "",
        notes: ""
      });
      await reload();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <Layout title="Licenses">
      <div className="form-grid">
        {Object.entries(form).map(([key, value]) => (
          <label key={key}>
            <span>{key}</span>
            <input
              value={value}
              onChange={(event) => setForm({ ...form, [key]: event.target.value })}
            />
          </label>
        ))}
        <button onClick={() => void submit()}>Create License</button>
      </div>
      {submitError && <div className="error-box">{submitError}</div>}
      {loading ? <div>Loading…</div> : <LicenseList items={data || []} />}
      {error && <div className="error-box">{error}</div>}
    </Layout>
  );
}
