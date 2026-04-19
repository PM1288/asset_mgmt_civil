import { Link } from "react-router-dom";
import type { DashboardQueueItem } from "../types";
import AppIcon, { type IconName } from "./AppIcon";

const queueIcons: Record<string, IconName> = {
  submitted_unassigned: "pending",
  under_review: "summary",
  waiting_for_inspection: "status",
  waiting_for_applicant_response: "documents",
  due_today: "calendar",
  overdue: "warning"
};

export default function QueueCard({ item, to }: { item: DashboardQueueItem; to: string }) {
  return (
    <Link className={`queue-card queue-card-${item.severity}`} to={to}>
      <div className="queue-card-header">
        <div className="queue-card-title">
          <span className="queue-card-icon">
            <AppIcon name={queueIcons[item.key] || "summary"} size={18} />
          </span>
          <h3>{item.label}</h3>
        </div>
        <span className="queue-card-count">{item.count}</span>
      </div>
      <p>{item.description}</p>
    </Link>
  );
}
