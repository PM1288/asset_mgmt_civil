import type { ReactNode } from "react";
import AppIcon, { type IconName } from "./AppIcon";

export default function SectionCard({
  title,
  icon,
  eyebrow,
  action,
  children
}: {
  title: string;
  icon?: IconName;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="section-card">
      <div className="section-card-header">
        <div className="section-card-heading">
          {icon ? (
            <span className="section-card-icon">
              <AppIcon name={icon} size={18} />
            </span>
          ) : null}
          <div>
            {eyebrow ? <p className="section-card-eyebrow">{eyebrow}</p> : null}
            <h3>{title}</h3>
          </div>
        </div>
        {action ? <div>{action}</div> : null}
      </div>
      <div className="section-card-body">{children}</div>
    </section>
  );
}
