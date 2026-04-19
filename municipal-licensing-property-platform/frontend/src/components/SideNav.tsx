import { NavLink } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import AppIcon, { type IconName } from "./AppIcon";

type NavItem = {
  label: string;
  icon: IconName;
  to: string;
  visible: boolean;
};

export default function SideNav({
  collapsed,
  mobileOpen,
  onNavigate,
  onToggleCollapse
}: {
  collapsed: boolean;
  mobileOpen: boolean;
  onNavigate: () => void;
  onToggleCollapse: () => void;
}) {
  const { subject, hasRole } = useAppContext();

  const items: NavItem[] = [
    { label: "Home", icon: "dashboard", to: "/dashboard", visible: true },
    { label: "Properties", icon: "property", to: "/properties", visible: true },
    { label: "Applications", icon: "license", to: "/licenses", visible: true },
    { label: "Service status", icon: "status", to: "/health", visible: true },
    {
      label: "Support tools",
      icon: "support",
      to: "/admin/diagnostics",
      visible: hasRole("municipal-admin", "operator", "auditor")
    },
    {
      label: "Activity history",
      icon: "audit",
      to: "/admin/audit",
      visible: hasRole("municipal-admin", "operator", "auditor")
    }
  ];

  return (
    <aside
      className={[
        "app-sidebar",
        collapsed ? "app-sidebar-collapsed" : "",
        mobileOpen ? "app-sidebar-open" : ""
      ].join(" ")}
    >
      <div className="app-sidebar-brand">
        <div className="app-sidebar-branding">
          <span className="app-brand-mark">
            <AppIcon name="brand" size={22} />
          </span>
          <div>
            <p className="app-sidebar-kicker">City services</p>
            <h1>{collapsed ? "CS" : "Civic Services"}</h1>
            {!collapsed ? <p className="app-sidebar-tagline">Property and licence applications</p> : null}
          </div>
        </div>
        <button
          type="button"
          className="icon-button app-sidebar-collapse"
          onClick={onToggleCollapse}
          aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
        >
          <AppIcon name={collapsed ? "expand" : "collapse"} size={16} />
        </button>
      </div>
      <div className="app-sidebar-user">
        {collapsed ? (
          <strong>{subject.username.slice(0, 2).toUpperCase()}</strong>
        ) : (
          <>
            <span className="app-sidebar-user-label">Signed in</span>
            <strong>{subject.username}</strong>
            <span>{subject.email || "Municipal account"}</span>
          </>
        )}
      </div>
      <nav className="app-sidebar-nav" aria-label="Primary">
        {items
          .filter((item) => item.visible)
          .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                ["nav-item", isActive ? "nav-item-active" : ""].join(" ")
              }
              onClick={onNavigate}
            >
              <span className="nav-item-icon" aria-hidden="true">
                <AppIcon name={item.icon} size={18} />
              </span>
              {!collapsed ? <span>{item.label}</span> : null}
            </NavLink>
          ))}
      </nav>
    </aside>
  );
}
