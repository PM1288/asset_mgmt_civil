import { useState } from "react";
import { createProperty, listProperties } from "../api/properties";
import PropertyList from "../components/PropertyList";
import Layout from "../components/Layout";
import { useAsync } from "../hooks/useAsync";

export default function PropertiesPage() {
  const { data, error, loading, reload } = useAsync(listProperties, []);
  const [form, setForm] = useState({
    property_number: "",
    ward_code: "",
    address_line_1: "",
    city: "Pune",
    district: "Pune",
    state: "Maharashtra",
    status: "active",
    use_type: "commercial",
    owner_name: "",
    owner_contact: ""
  });
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function submit() {
    setSubmitError(null);
    try {
      await createProperty(form);
      setForm({
        property_number: "",
        ward_code: "",
        address_line_1: "",
        city: "Pune",
        district: "Pune",
        state: "Maharashtra",
        status: "active",
        use_type: "commercial",
        owner_name: "",
        owner_contact: ""
      });
      await reload();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <Layout title="Properties">
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
        <button onClick={() => void submit()}>Create Property</button>
      </div>
      {submitError && <div className="error-box">{submitError}</div>}
      {loading ? <div>Loading…</div> : <PropertyList items={data || []} />}
      {error && <div className="error-box">{error}</div>}
    </Layout>
  );
}
