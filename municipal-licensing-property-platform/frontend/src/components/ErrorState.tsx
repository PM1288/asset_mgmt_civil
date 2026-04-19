import type { ReactNode } from "react";
import AppIcon, { type IconName } from "./AppIcon";

export default function ErrorState({
  title,
  description,
  icon = "warning",
  action
}: {
  title?: string;
  description: string;
  icon?: IconName;
  action?: ReactNode;
}) {
  return (
    <div className="error-state">
      <span className="state-icon">
        <AppIcon name={icon} size={20} />
      </span>
      <h3>{title || "Something went wrong"}</h3>
      <p>{description}</p>
      {action ? <div className="error-state-action">{action}</div> : null}
    </div>
  );
}
