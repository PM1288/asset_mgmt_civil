import type { PropertyRecord } from "../types";

export default function PropertyList({ items }: { items: PropertyRecord[] }) {
  if (!items.length) {
    return <div>No properties found.</div>;
  }
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Number</th>
          <th>Ward</th>
          <th>Address</th>
          <th>Status</th>
          <th>Owner</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.property_number}</td>
            <td>{item.ward_code}</td>
            <td>{item.address_line_1}</td>
            <td>{item.status}</td>
            <td>{item.owner_name}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
