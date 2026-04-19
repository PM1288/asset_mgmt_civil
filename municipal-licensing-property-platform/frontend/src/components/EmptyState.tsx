import type { ReactNode } from "react";
import AppIcon, { type IconName } from "./AppIcon";

export default function EmptyState({
  title,
  description,
  icon = "documents",
  action
}: {
  title: string;
  description: string;
  icon?: IconName;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="state-icon">
        <AppIcon name={icon} size={20} />
      </span>
      <h3>{title}</h3>
      <p>{description}</p>
      {action ? <div className="empty-state-action">{action}</div> : null}
    </div>
  );
}
