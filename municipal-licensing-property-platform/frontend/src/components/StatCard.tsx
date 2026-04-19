import { Link } from "react-router-dom";
import AppIcon, { type IconName } from "./AppIcon";

export default function StatCard({
  title,
  value,
  helper,
  icon,
  to
}: {
  title: string;
  value: string;
  helper: string;
  icon?: IconName;
  to: string;
}) {
  return (
    <Link className="stat-card" to={to}>
      <div className="stat-card-header">
        <span className="stat-card-label">{title}</span>
        {icon ? (
          <span className="stat-card-icon">
            <AppIcon name={icon} size={18} />
          </span>
        ) : null}
      </div>
      <strong className="stat-card-value">{value}</strong>
      <span className="stat-card-helper">{helper}</span>
    </Link>
  );
}
