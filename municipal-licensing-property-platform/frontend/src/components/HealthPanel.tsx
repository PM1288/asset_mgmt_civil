import type { HealthEnvelope } from "../types";

type Props = {
  data?: HealthEnvelope | null;
  error?: string | null;
};

export default function HealthPanel({ data, error }: Props) {
  if (error) {
    return <div className="error-box">{error}</div>;
  }
  if (!data) {
    return <div>Loading health data…</div>;
  }
  return (
    <div className="grid">
      {data.components.map((component) => (
        <div key={component.name} className={`health-card ${component.ok ? "ok" : "bad"}`}>
          <strong>{component.name}</strong>
          <div>{component.ok ? "OK" : "Degraded"}</div>
          <small>{component.detail}</small>
        </div>
      ))}
    </div>
  );
}
