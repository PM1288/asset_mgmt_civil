import { humanStatus, statusTone } from "../utils/status";

export default function StatusBadge({ status, label }: { status: string; label?: string }) {
  const tone = statusTone(status);
  return <span className={`status-badge status-badge-${tone}`}>{label || humanStatus(status)}</span>;
}
