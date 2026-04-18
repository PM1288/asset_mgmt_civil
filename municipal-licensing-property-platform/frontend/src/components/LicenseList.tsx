import type { LicenseRecord } from "../types";

export default function LicenseList({ items }: { items: LicenseRecord[] }) {
  if (!items.length) {
    return <div>No licenses found.</div>;
  }
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Application</th>
          <th>Property ID</th>
          <th>Type</th>
          <th>Status</th>
          <th>Applicant</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.application_number}</td>
            <td>{item.property_id}</td>
            <td>{item.license_type}</td>
            <td>{item.status}</td>
            <td>{item.applicant_name}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
